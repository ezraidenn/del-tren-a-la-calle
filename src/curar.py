"""Capa silver: cura las tablas de datos/para-etl y documenta su calidad.

Para cada tabla de src/tablas.py:
1. Normaliza texto (espacios, Unicode NFC), tipos (claves como texto, números,
   fechas ISO 8601, booleanos) y vacíos.
2. Aplica las reglas de calidad. Cada renglón que no las cumple se guarda en
   datos/rechazados/<tabla>.csv con la regla y el motivo; nunca se borra.
3. Escribe la tabla curada en datos/curados/<NN_tipo>/<N.M_fuente>/<tabla>.parquet
   y .csv.
4. Concilia cantidades: original -> para-etl -> curado + rechazados.

Reglas generales (en este orden):
- R1 duplicado exacto: el renglón repite a otro en todas sus columnas.
- R2 clave nula: alguna columna de la clave está vacía.
- R3 clave duplicada: la clave ya apareció en un renglón anterior.
- R4 coordenada incompleta: trae lat o lon, pero no ambas.
- R5 coordenada fuera del área: lat/lon fuera de los 5 estados del Tren Maya.
- R6 valor negativo: montos, metros, precios, tarifas, costos, duraciones o
  distancias menores que cero.
Reglas propias por tabla (declaradas en src/tablas.py):
- fuera_de_merida: se rechaza el anuncio que declara otro municipio, o que no
  declara municipio y tiene coordenadas fuera de Mérida. Si no declara
  municipio se asigna Mérida (municipio_imputado) y se marca si la ubicación
  se verificó con coordenadas (ubicacion_verificada).
- coordenada_opcional: la R5 no rechaza el registro; borra la coordenada
  fuera del área y lo marca en coordenada_descartada.
- colonia_normalizada: agrega la colonia en mayúsculas, sin acentos ni el
  prefijo «MERIDA», para agrupar variantes como «CENTRO» y «MERIDA CENTRO».

Salidas de documentación (las comparte la capa gold):
- catalogo_tablas.csv, diccionario_columnas.csv
- reportes/conciliacion.csv, reportes/calidad_columnas.csv, reportes/calidad.md

Uso: python src/curar.py
"""

from __future__ import annotations

import csv
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tablas  # noqa: E402

RAIZ = tablas.RAIZ
CURADOS = RAIZ / "datos" / "curados"
RECHAZADOS = RAIZ / "datos" / "rechazados"
REPORTES = RAIZ / "reportes"
DESCRIPCIONES = RAIZ / "src" / "descripciones.csv"

# Rectángulo que contiene Campeche, Chiapas, Quintana Roo, Tabasco y Yucatán.
LAT = (14.4, 21.8)
LON = (-94.3, -86.6)
# Comisarías y localidades que pertenecen al municipio de Mérida.
LOCALIDADES_MERIDA = {
    "MERIDA", "CAUCEL", "CHOLUL", "CHABLEKAL", "KOMCHEN", "DZITYA", "SITPACH", "TIXCACAL", "MOLAS",
    "TEMOZON NORTE", "XCANATUN", "SAN JOSE TZAL", "DZUNUNCAN", "COSGAYA", "NOC AC", "SUSULA",
    "SAN ANTONIO TZACALA", "OXCUM", "XCUNYA", "YAXNIC", "SANTA GERTRUDIS COPO", "TAMANCHE",
    "SAN PEDRO CHIMAY", "DZIBILCHALTUN", "CHALMUCH", "TEXAN CAMARA", "SANTA CRUZ PALOMEQUE",
}
# Rectángulo del municipio de Mérida, con margen.
LAT_MERIDA = (20.70, 21.35)
LON_MERIDA = (-89.85, -89.40)

CODIGOS = {"ent", "mun", "loc", "ageb", "mza", "entidad", "cve_ent", "cve_mun", "cve_ageb", "cve_geo",
           "clave", "clave_ent", "codigo_postal", "folio", "stop_id", "trip_id", "service_id", "shape_id",
           "id_anuncio", "circulacion", "corrida", "tramo", "ciclo_reporte"}
PREFIJOS_NO_NEGATIVOS = ("monto", "metros", "precio", "tarifa", "costo", "duracion", "distancia",
                         "comprometido", "devengado", "ejercido", "pagado")
PATRON_FECHA = re.compile(r"^(fecha|periodo_inicio|periodo_fin|vigencia_inicio|vigencia_fin)")


# --- Utilidades ------------------------------------------------------------

def sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def normalizar_texto(serie: pd.Series) -> pd.Series:
    s = serie.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    s = s.map(lambda x: unicodedata.normalize("NFC", x) if isinstance(x, str) else x).astype("string")
    return s.mask(s == "")


def es_codigo(col: str) -> bool:
    return col in CODIGOS or col.startswith(("cvegeo", "cve_", "id_"))


def tipar(df: pd.DataFrame, clave: list[str]) -> pd.DataFrame:
    """Asigna tipos: claves y códigos como texto, fechas ISO, booleanos y números."""
    for col in df.columns:
        s = df[col]
        if col in clave or es_codigo(col) or col in {"lat_texto", "lon_texto"} or col.endswith("_texto"):
            continue
        no_nulos = s.dropna()
        if no_nulos.empty:
            continue
        if PATRON_FECHA.match(col):
            fechas = pd.to_datetime(no_nulos, errors="coerce", format="mixed")
            if fechas.notna().all():
                df[col] = pd.to_datetime(s, errors="coerce", format="mixed").dt.strftime("%Y-%m-%d").astype("string")
            continue
        if set(no_nulos.str.lower().unique()) <= {"true", "false"}:
            df[col] = s.str.lower().map({"true": True, "false": False}).astype("boolean")
            continue
        numeros = pd.to_numeric(no_nulos.str.replace(",", "", regex=False), errors="coerce")
        if numeros.notna().all():
            convertido = pd.to_numeric(s.str.replace(",", "", regex=False), errors="coerce")
            if (numeros % 1 == 0).all() and numeros.abs().max() < 2**53:
                df[col] = convertido.astype("Int64")
            else:
                df[col] = convertido.astype("Float64")
    return df


def rango_cobertura(df: pd.DataFrame, cobertura) -> tuple[str, str]:
    if isinstance(cobertura, tuple):
        return cobertura
    s = df[cobertura].dropna().astype(str)
    return (s.min(), s.max()) if not s.empty else ("", "")


def ruta_curado(spec: dict, extension: str) -> Path:
    partes = Path(spec["archivo"]).parts  # datos/para-etl/NN_tipo/N.M_fuente/archivo
    return CURADOS / partes[2] / partes[3] / f"{spec['tabla']}.{extension}"


# --- Reglas ----------------------------------------------------------------

def aplicar_reglas(df: pd.DataFrame, spec: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    rechazos = []

    def rechazar(mascara: pd.Series, regla: str, motivo: str) -> None:
        nonlocal df
        if mascara.any():
            r = df[mascara].copy()
            r.insert(0, "motivo", motivo)
            r.insert(0, "regla", regla)
            rechazos.append(r)
            df = df[~mascara]

    clave = spec["clave"]
    rechazar(df.duplicated(keep="first"), "R1", "duplicado exacto de un renglón anterior")
    rechazar(df[clave].isna().any(axis=1), "R2", f"clave nula ({', '.join(clave)})")
    rechazar(df.duplicated(subset=clave, keep="first"), "R3", "clave duplicada; se conserva la primera aparición")
    if {"lat", "lon"} <= set(df.columns):
        lat = pd.to_numeric(df["lat"], errors="coerce")
        lon = pd.to_numeric(df["lon"], errors="coerce")
        rechazar(lat.isna() ^ lon.isna(), "R4", "coordenada incompleta: falta lat o lon")
        lat, lon = lat.loc[df.index], lon.loc[df.index]
        fuera = lat.notna() & ~(lat.between(*LAT) & lon.between(*LON))
        if "coordenada_opcional" in spec["reglas"]:
            # La coordenada es un atributo opcional: se descarta solo ella y se
            # conserva el registro, marcado en coordenada_descartada.
            df = df.assign(coordenada_descartada=fuera.astype("boolean"))
            df.loc[fuera, ["lat", "lon"]] = pd.NA
        else:
            rechazar(fuera, "R5", "coordenada fuera de los 5 estados del Tren Maya")
    for col in df.columns:
        if col.startswith(PREFIJOS_NO_NEGATIVOS) and pd.api.types.is_numeric_dtype(df[col]):
            rechazar(df[col].fillna(0) < 0, "R6", f"valor negativo en {col}")

    if "fuera_de_merida" in spec["reglas"]:
        municipio = df["municipio"].fillna("").map(lambda x: sin_acentos(str(x)).upper())
        en_lista = municipio.map(lambda m: any(loc in m for loc in LOCALIDADES_MERIDA))
        rechazar((municipio != "") & ~en_lista, "P1",
                 "el anuncio declara un municipio distinto de Mérida")
        municipio = municipio.loc[df.index]
        lat = pd.to_numeric(df["lat"], errors="coerce")
        lon = pd.to_numeric(df["lon"], errors="coerce")
        en_merida = lat.between(*LAT_MERIDA) & lon.between(*LON_MERIDA)
        rechazar((municipio == "") & lat.notna() & ~en_merida, "P1",
                 "el anuncio no trae municipio y sus coordenadas están fuera de Mérida")
        municipio = municipio.loc[df.index]
        lat, en_merida = lat.loc[df.index], en_merida.loc[df.index]
        # Sin municipio: se asigna Mérida (es el listado de Mérida) y se marca
        # si la ubicación se pudo verificar con coordenadas.
        df = df.assign(
            municipio_imputado=(municipio == "").astype("boolean"),
            municipio=df["municipio"].fillna("MERIDA"),
            ubicacion_verificada=(lat.notna() & en_merida).astype("boolean"),
        )
    if "colonia_normalizada" in spec["reglas"]:
        col = df["colonia"].fillna("").map(lambda x: sin_acentos(str(x)).upper().strip())
        col = col.str.replace(r"^(MERIDA|COL\.?|COLONIA|FRACC\.?|FRACCIONAMIENTO)\s+", "", regex=True)
        col = col.str.replace(r"\s+[A-Z]\s*-\s*\d+$", "", regex=True).str.strip()
        df = df.assign(colonia_normalizada=col.mask(col == "").astype("string"))

    rechazados = pd.concat(rechazos) if rechazos else pd.DataFrame(columns=["regla", "motivo", *df.columns])
    return df, rechazados


# --- Documentación compartida ---------------------------------------------

def escribir_csv(df: pd.DataFrame, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8", lineterminator="\n")


def actualizar(ruta: Path, filas: pd.DataFrame, capa: str) -> None:
    """Reemplaza en un CSV de documentación los renglones de una capa."""
    if ruta.exists():
        previo = pd.read_csv(ruta, dtype=str, keep_default_na=False)
        previo = previo[previo["capa"] != capa]
        filas = pd.concat([previo, filas.astype(str)], ignore_index=True)
    escribir_csv(filas.sort_values(["capa", "tabla"], kind="stable"), ruta)


def perfil_columnas(df: pd.DataFrame, tabla: str, capa: str) -> pd.DataFrame:
    filas = []
    for col in df.columns:
        s = df[col]
        no_nulos = s.dropna()
        numerico = pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)
        filas.append({
            "capa": capa, "tabla": tabla, "columna": col, "tipo": str(s.dtype),
            "nulos": int(s.isna().sum()), "nulos_pct": round(100 * s.isna().mean(), 2) if len(s) else 0,
            "distintos": int(no_nulos.nunique()),
            "minimo": no_nulos.min() if numerico and len(no_nulos) else "",
            "maximo": no_nulos.max() if numerico and len(no_nulos) else "",
            "ejemplo": str(no_nulos.iloc[0])[:80] if len(no_nulos) else "",
        })
    return pd.DataFrame(filas)


def leer_descripciones() -> dict[tuple[str, str], dict]:
    if not DESCRIPCIONES.exists():
        return {}
    with open(DESCRIPCIONES, encoding="utf-8", newline="") as f:
        return {(r["archivo"], r["columna"]): r for r in csv.DictReader(f)}


def ficha_catalogo(spec: dict, df: pd.DataFrame, capa: str, fuentes: dict) -> dict:
    inicio, fin = rango_cobertura(df, spec["cobertura"])
    ids = spec["id_fuente"].split(";")
    fuente = [fuentes.get(i, {}) for i in ids]
    return {
        "capa": capa, "tabla": spec["tabla"], "id_fuente": spec["id_fuente"], "formato": spec["formato"],
        "archivo_parquet": str(spec["_parquet"].relative_to(RAIZ)).replace("\\", "/"),
        "archivo_csv": str(spec["_csv"].relative_to(RAIZ)).replace("\\", "/"),
        "clave": ";".join(spec["clave"]), "granularidad": spec["granularidad"],
        "cobertura_inicio": inicio, "cobertura_fin": fin, "territorio": spec["territorio"],
        "unidad": spec["unidad"], "fuente": " | ".join(f.get("nombre", "") for f in fuente),
        "url_original": " | ".join(f.get("url_original", "") for f in fuente),
        "licencia": " | ".join(dict.fromkeys(f.get("licencia", "") for f in fuente)),
        "version_fuente": spec["version_fuente"], "filas": len(df), "columnas": len(df.columns),
        "responsable": spec["responsable"],
    }


def filas_diccionario(spec: dict, df: pd.DataFrame, capa: str, descripciones: dict,
                      origen: str) -> list[dict]:
    filas = []
    for col in df.columns:
        d = descripciones.get((origen, col), {})
        filas.append({
            "capa": capa, "tabla": spec["tabla"], "columna": col, "tipo": str(df[col].dtype),
            "es_clave": col in spec["clave"],
            "descripcion": d.get("descripcion", ""), "unidad": d.get("unidad", ""),
            "nulos_pct": round(100 * df[col].isna().mean(), 2) if len(df) else 0,
            "origen_descripcion": d.get("origen_descripcion", ""),
        })
    return filas


def leer_fuentes() -> dict:
    with open(RAIZ / "fuentes.csv", encoding="utf-8", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


# --- Proceso -----------------------------------------------------------------

DESCRIPCIONES_PROPIAS = {
    "coordenada_descartada": {"descripcion": "Verdadero si la coordenada publicada caía fuera de los 5 estados "
                                             "del Tren Maya y se borró; el registro se conserva",
                              "unidad": "booleano", "origen_descripcion": "regla coordenada_opcional de src/curar.py"},
    "municipio_imputado": {"descripcion": "Verdadero si el anuncio no traía municipio y se le asignó Mérida por "
                                          "pertenecer al listado de Mérida", "unidad": "booleano",
                           "origen_descripcion": "regla fuera_de_merida de src/curar.py"},
    "ubicacion_verificada": {"descripcion": "Verdadero si las coordenadas del anuncio caen dentro del municipio "
                                            "de Mérida", "unidad": "booleano",
                             "origen_descripcion": "regla fuera_de_merida de src/curar.py"},
    "colonia_normalizada": {"descripcion": "Colonia en mayúsculas, sin acentos ni prefijos (MERIDA, COL., FRACC.) "
                                           "para agrupar variantes del mismo nombre",
                            "unidad": "texto", "origen_descripcion": "regla colonia_normalizada de src/curar.py"},
}


def main() -> int:
    fuentes = leer_fuentes()
    descripciones = leer_descripciones()
    catalogo, diccionario, perfiles, conciliacion = [], [], [], []
    faltan_desc = 0
    for spec in tablas.TABLAS:
        entrada = pd.read_csv(RAIZ / spec["archivo"], dtype=str, keep_default_na=False, low_memory=False)
        n_etl = len(entrada)
        df = entrada.apply(normalizar_texto)
        df = tipar(df, spec["clave"])
        df, rechazados = aplicar_reglas(df, spec)

        spec["_parquet"], spec["_csv"] = ruta_curado(spec, "parquet"), ruta_curado(spec, "csv")
        spec["_parquet"].parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(spec["_parquet"], index=False)
        escribir_csv(df, spec["_csv"])
        escribir_csv(rechazados, RECHAZADOS / f"{spec['tabla']}.csv")

        n_original = spec["conteo_original"]() if spec["conteo_original"] else None
        cuadra_capas = n_etl == len(df) + len(rechazados)
        cuadra_original = "" if n_original is None else n_original == n_etl
        conciliacion.append({
            "capa": "silver", "tabla": spec["tabla"], "id_fuente": spec["id_fuente"],
            "filas_original": "" if n_original is None else n_original, "filas_para_etl": n_etl,
            "filas_curado": len(df), "filas_rechazadas": len(rechazados),
            "cuadra_original_para_etl": cuadra_original, "cuadra_para_etl_curado": cuadra_capas,
            "nota": spec["nota_conciliacion"] or ("" if n_original is not None else "Sin conteo independiente del original."),
        })
        catalogo.append(ficha_catalogo(spec, df, "silver", fuentes))
        perfiles.append(perfil_columnas(df, spec["tabla"], "silver"))
        filas = filas_diccionario(spec, df, "silver", {**descripciones,
                                  **{(spec["archivo"], k): v for k, v in DESCRIPCIONES_PROPIAS.items()}},
                                  spec["archivo"])
        faltan_desc += sum(1 for f in filas if not f["descripcion"])
        diccionario.extend(filas)
        marca = "OK" if cuadra_capas and cuadra_original in ("", True) else "REVISAR"
        print(f"[{marca}] {spec['tabla']}: original {n_original}, para-etl {n_etl}, "
              f"curado {len(df)}, rechazados {len(rechazados)}")

    actualizar(RAIZ / "catalogo_tablas.csv", pd.DataFrame(catalogo), "silver")
    actualizar(RAIZ / "diccionario_columnas.csv", pd.DataFrame(diccionario), "silver")
    actualizar(REPORTES / "conciliacion.csv", pd.DataFrame(conciliacion), "silver")
    actualizar(REPORTES / "calidad_columnas.csv", pd.concat(perfiles), "silver")
    if faltan_desc:
        print(f"AVISO: {faltan_desc} columnas sin descripción en src/descripciones.csv")
    malos = [c for c in conciliacion if not c["cuadra_para_etl_curado"] or c["cuadra_original_para_etl"] is False]
    print(f"{len(conciliacion)} tablas curadas; {len(malos)} con conteos que no cuadran")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
