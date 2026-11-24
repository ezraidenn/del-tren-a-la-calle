"""Carga las tablas curadas (silver) y gold a PostgreSQL, en un esquema staging.

Carga repetible e incremental:
- Cada tabla del catálogo (catalogo_tablas.csv) se carga desde su Parquet.
- La tabla de control <esquema>._cargas guarda el SHA-256 del Parquet cargado.
  Si el archivo no cambió, la tabla no se vuelve a cargar.
- Si cambió, se reemplaza completa dentro de una transacción (TRUNCATE + COPY).
  Si cambiaron las columnas, la tabla se vuelve a crear.
- Después de cargar, compara count(*) en la base con las filas del Parquet y
  con el catálogo. Si no coinciden, deshace la transacción.
- La clave primaria es la clave declarada en el catálogo.

La conexión usa las variables estándar de PostgreSQL: PGHOST, PGPORT,
PGDATABASE, PGUSER y PGPASSWORD. Ninguna credencial va en el código.

Uso:
    python src/cargar_staging.py                   # carga incremental en e8_staging
    python src/cargar_staging.py --forzar          # recarga todo
    python src/cargar_staging.py --solo-sql        # solo escribe sql/staging.sql
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CATALOGO = RAIZ / "catalogo_tablas.csv"
SQL = RAIZ / "sql" / "staging.sql"
PATRON_FECHA = re.compile(r"^(fecha|periodo_inicio|periodo_fin|vigencia_inicio|vigencia_fin)")


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def ident(nombre: str) -> str:
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", nombre):
        raise ValueError(f"Nombre no válido para PostgreSQL: {nombre}")
    return nombre


def tipo_pg(col: str, serie: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(serie):
        return "boolean"
    if pd.api.types.is_integer_dtype(serie):
        return "bigint"
    if pd.api.types.is_float_dtype(serie):
        return "double precision"
    if PATRON_FECHA.match(col) and serie.dropna().astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        return "date"
    return "text"


def leer_catalogo() -> list[dict]:
    with open(CATALOGO, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ddl_tabla(esquema: str, ficha: dict, df: pd.DataFrame) -> str:
    columnas = [f"    {ident(c)} {tipo_pg(c, df[c])}" for c in df.columns]
    clave = ", ".join(ident(c) for c in ficha["clave"].split(";"))
    comentario = (f"{ficha['granularidad']}; {ficha['territorio']}; cobertura {ficha['cobertura_inicio']} a "
                  f"{ficha['cobertura_fin']}; fuente {ficha['id_fuente']}").replace("'", "''")
    return (f"CREATE TABLE IF NOT EXISTS {esquema}.{ident(ficha['tabla'])} (\n" + ",\n".join(columnas)
            + f",\n    PRIMARY KEY ({clave})\n);\n"
            + f"COMMENT ON TABLE {esquema}.{ident(ficha['tabla'])} IS '{comentario}';\n")


def ddl_control(esquema: str) -> str:
    return (f"CREATE SCHEMA IF NOT EXISTS {esquema};\n"
            f"CREATE TABLE IF NOT EXISTS {esquema}._cargas (\n"
            "    tabla text NOT NULL,\n    capa text NOT NULL,\n    archivo text NOT NULL,\n"
            "    sha256 char(64) NOT NULL,\n    filas bigint NOT NULL,\n    cargado_utc timestamptz NOT NULL,\n"
            "    PRIMARY KEY (tabla, sha256)\n);\n")


def escribir_sql(esquema: str, fichas: list[dict]) -> None:
    partes = [f"-- Esquema staging del equipo E8. Generado por src/cargar_staging.py --solo-sql.\n"
              f"-- Una tabla por cada renglón de catalogo_tablas.csv.\n\n", ddl_control(esquema), "\n"]
    for ficha in fichas:
        df = pd.read_parquet(RAIZ / ficha["archivo_parquet"])
        partes.append(f"-- {ficha['capa']}: {ficha['tabla']}\n{ddl_tabla(esquema, ficha, df)}\n")
    SQL.parent.mkdir(exist_ok=True)
    SQL.write_text("".join(partes), encoding="utf-8", newline="\n")
    print(f"Escrito {SQL.relative_to(RAIZ)} con {len(fichas)} tablas")


def cargar(esquema: str, fichas: list[dict], forzar: bool) -> int:
    import psycopg

    errores = 0
    with psycopg.connect() as con:
        con.execute(ddl_control(esquema))
        con.commit()
        for ficha in fichas:
            tabla = ident(ficha["tabla"])
            ruta = RAIZ / ficha["archivo_parquet"]
            huella = sha256_de(ruta)
            ya = con.execute(f"SELECT 1 FROM {esquema}._cargas WHERE tabla = %s AND sha256 = %s",
                             (tabla, huella)).fetchone()
            if ya and not forzar:
                print(f"  sin cambios {tabla}")
                continue
            df = pd.read_parquet(ruta)
            try:
                with con.transaction():
                    existentes = [r[0] for r in con.execute(
                        "SELECT column_name FROM information_schema.columns WHERE table_schema = %s "
                        "AND table_name = %s ORDER BY ordinal_position", (esquema, tabla)).fetchall()]
                    if existentes and existentes != list(df.columns):
                        con.execute(f"DROP TABLE {esquema}.{tabla}")
                    con.execute(ddl_tabla(esquema, ficha, df))
                    con.execute(f"TRUNCATE {esquema}.{tabla}")
                    buffer = io.StringIO()
                    df.to_csv(buffer, index=False, header=False, na_rep="\\N")
                    buffer.seek(0)
                    columnas = ", ".join(ident(c) for c in df.columns)
                    with con.cursor().copy(f"COPY {esquema}.{tabla} ({columnas}) FROM STDIN "
                                           "WITH (FORMAT csv, NULL '\\N')") as copia:
                        copia.write(buffer.read())
                    en_base = con.execute(f"SELECT count(*) FROM {esquema}.{tabla}").fetchone()[0]
                    esperado = int(ficha["filas"])
                    if not (en_base == len(df) == esperado):
                        raise RuntimeError(f"conteo distinto: base {en_base}, parquet {len(df)}, catálogo {esperado}")
                    con.execute(f"INSERT INTO {esquema}._cargas VALUES (%s, %s, %s, %s, %s, %s)",
                                (tabla, ficha["capa"], ficha["archivo_parquet"], huella, en_base,
                                 datetime.now(timezone.utc)))
                print(f"  cargada {tabla}: {en_base:,} filas (cuadra con el catálogo)")
            except Exception as e:  # la transacción ya se deshizo
                errores += 1
                print(f"  ERROR {tabla}: {e}")
    return errores


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--esquema", default="e8_staging")
    parser.add_argument("--forzar", action="store_true", help="recarga aunque el archivo no haya cambiado")
    parser.add_argument("--solo-sql", action="store_true", help="solo genera sql/staging.sql")
    args = parser.parse_args()
    esquema = ident(args.esquema)
    fichas = leer_catalogo()
    escribir_sql(esquema, fichas)
    if args.solo_sql:
        return 0
    errores = cargar(esquema, fichas, args.forzar)
    print(f"{len(fichas)} tablas revisadas, {errores} con error")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
