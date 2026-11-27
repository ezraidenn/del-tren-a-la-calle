"""Revisa que la entrega cumpla las reglas de aceptación del servidor.

Reglas:
1. fuentes.csv tiene exactamente 27 filas, ids EX-01.1 a EX-09.3, columnas
   completas y un estado válido (real, derivado, simulado, pendiente).
2. Cada archivo de manifest.csv existe y su SHA-256 coincide.
3. Toda fuente con estado real o derivado tiene archivos en el manifiesto.
4. La entrega de E8 no lleva datos simulados: ninguna fuente con estado
   simulado, ningún archivo cuya ruta diga «simulad» o SIMULADO_, con capa
   «simulado» o con id de fuente terminado en -SIM, y ninguna tabla así en
   el catálogo. El estado «simulado» lo acepta el servidor, pero E8 no lo usa.
5. No hay rutas locales de Windows (carpeta Users de una unidad) ni URL de
   archivo local en los textos del repositorio.
6. Los datos propios de campo/ no traen correos, teléfonos ni CURP.
7. Archivos de más de 50 MB y páginas crudas con datos personales o derechos
   reservados: declarados en externos.csv con motivo y sha256, fuera de git
   y sin rastro en el historial.
8. Las carpetas NN_tipo/N.M_fuente usan el mismo número de subtema.
9. catalogo_tablas.csv describe cada tabla curada con clave, granularidad,
   cobertura temporal, territorio, fuente, unidad, versión, formato y
   responsable, y sus archivos existen.
10. diccionario_columnas.csv documenta, con descripción y unidad, cada columna
    de cada tabla del catálogo.
11. reportes/conciliacion.csv: los conteos cuadran en todas las tablas y cada
    tabla curada tiene su archivo de registros rechazados.

Termina con código 1 si hay errores.

Sirve para cualquier equipo: el número de equipo se toma de fuentes.csv o se
pasa con --equipo. No depende de otros módulos del repositorio.

Uso:
    python src/validar_entrega.py                      # desde la raíz del repo
    python validar_entrega.py --raiz <carpeta> --equipo E5
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
EQUIPO = ""
ESTADOS = {"real", "derivado", "simulado", "pendiente"}
COLUMNAS = ["id", "subtema", "tipo_fuente", "nombre", "url_original", "licencia",
            "fecha_descarga", "estado", "carpeta"]
LIMITE_MB = 50

errores: list[str] = []
avisos: list[str] = []


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def git(*args: str) -> subprocess.CompletedProcess:
    """Corre git sin fsmonitor ni hooks: el .git/config de una entrega ajena
    podría ejecutar programas al leer el índice."""
    return subprocess.run(["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", *args],
                          cwd=RAIZ, capture_output=True)


def dentro_de_raiz(rel: str) -> Path | None:
    """Ruta absoluta de rel si queda dentro de la entrega; None si se sale (p. ej. con ../)."""
    ruta = (RAIZ / rel).resolve()
    try:
        ruta.relative_to(RAIZ)
    except ValueError:
        errores.append(f"ruta fuera de la entrega: {rel}")
        return None
    return ruta


def leer_csv(nombre: str) -> list[dict]:
    if not (RAIZ / nombre).exists():
        errores.append(f"falta {nombre}")
        return []
    with open(RAIZ / nombre, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def regla_fuentes() -> list[dict]:
    filas = leer_csv("fuentes.csv")
    if len(filas) != 27:
        errores.append(f"fuentes.csv tiene {len(filas)} filas; deben ser 27")
    esperados = {f"{EQUIPO}-{s:02d}.{n}" for s in range(1, 10) for n in range(1, 4)}
    ids = [f.get("id", "") for f in filas]
    if set(ids) != esperados or len(set(ids)) != len(ids):
        errores.append(f"ids de fuentes.csv incompletos o repetidos: faltan {sorted(esperados - set(ids))}")
    for f in filas:
        faltan = [c for c in COLUMNAS if c not in f]
        if faltan:
            errores.append(f"fuentes.csv no tiene las columnas {faltan}")
            break
        if f["estado"] not in ESTADOS:
            errores.append(f"{f['id']}: estado «{f['estado']}» no válido")
        if not f["url_original"].startswith("http"):
            errores.append(f"{f['id']}: url_original vacía o no es URL")
        if f["estado"] in {"real", "derivado"} and not f["fecha_descarga"]:
            errores.append(f"{f['id']}: falta fecha_descarga")
        if not (RAIZ / f["carpeta"]).exists():
            errores.append(f"{f['id']}: no existe la carpeta {f['carpeta']}")
    return filas


def regla_manifest(fuentes: list[dict]) -> None:
    filas = leer_csv("manifest.csv")
    externos = {f["archivo"] for f in leer_csv("externos.csv")}
    con_archivos = set()
    for f in filas:
        ruta = dentro_de_raiz(f["archivo"])
        if ruta is None:
            continue
        for ident in f.get("id_fuente", "").split(";"):
            con_archivos.add(ident)
        if not ruta.exists():
            if f["archivo"] in externos:
                avisos.append(f"externo no presente en local: {f['archivo']}")
            else:
                errores.append(f"manifest: no existe {f['archivo']}")
            continue
        if sha256_de(ruta) != f.get("sha256", "").lower():
            errores.append(f"manifest: el hash no coincide en {f['archivo']} (hay que regenerar el manifiesto)")
        es_original = f.get("capa") == "original" or "/originales/" in f"/{f['archivo']}"
        if es_original and not f.get("url"):
            errores.append(f"manifest: original sin URL {f['archivo']}")
        ident = f.get("id_fuente", "")
        if ("simulad" in f["archivo"].lower() or "SIMULADO_" in f["archivo"]
                or f.get("capa") == "simulado" or ident.endswith("-SIM")):
            errores.append(f"{f['archivo']}: la entrega no lleva datos simulados")
    for x in fuentes:
        if x["estado"] == "simulado":
            errores.append(f"{x['id']}: la entrega no lleva fuentes simuladas")
        if x["estado"] in {"real", "derivado"} and x["id"] not in con_archivos:
            errores.append(f"{x['id']}: estado {x['estado']} sin archivos en manifest.csv")


def archivos_versionados() -> list[str]:
    salida = git("ls-files", "-z")
    if salida.returncode != 0:
        avisos.append("la entrega no es un repositorio git: se omiten las reglas de git e historial")
        return []
    return [p for p in salida.stdout.decode("utf-8").split("\0") if p]


def regla_rutas_locales(versionados: list[str]) -> None:
    patron = re.compile(r"[A-Za-z]:\\Users\\|file:/{3}")
    for rel in versionados:
        if rel.startswith("datos/originales/") or not rel.endswith((".md", ".py", ".csv", ".json", ".txt", ".sql")):
            continue
        ruta = dentro_de_raiz(rel)
        if ruta is None:
            continue
        if ruta.exists() and ruta.stat().st_size < 5_000_000 and patron.search(ruta.read_text(encoding="utf-8", errors="ignore")):
            errores.append(f"ruta local en {rel}")


def regla_datos_personales() -> None:
    correo = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
    telefono = re.compile(r"(?<!\d)(?:\+?52[\s-]?)?(?:\d[\s-]?){10}(?!\d)")
    curp = re.compile(r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b")
    for ruta in (RAIZ / "campo").rglob("*.csv"):
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        for nombre, patron in [("correo", correo), ("teléfono", telefono), ("CURP", curp)]:
            if patron.search(texto):
                errores.append(f"posible {nombre} en {ruta.relative_to(RAIZ)}")


def regla_tamanos(versionados: list[str]) -> None:
    externos = {f["archivo"] for f in leer_csv("externos.csv")}
    for rel in versionados:
        ruta = dentro_de_raiz(rel)
        if ruta is None:
            continue
        if ruta.exists() and ruta.stat().st_size > LIMITE_MB * 1024 * 1024:
            errores.append(f"archivo de más de {LIMITE_MB} MB versionado en git: {rel}")
    for rel in externos:
        if rel in versionados:
            errores.append(f"externo versionado en git: {rel}")
    for f in leer_csv("externos.csv"):
        if not f.get("motivo") or len(f.get("sha256", "")) != 64:
            errores.append(f"externos.csv: falta motivo o sha256 en {f['archivo']}")
        if f.get("motivo") in {"privacidad", "derechos"}:
            historial = git("log", "--all", "--format=%h", "--", f["archivo"]).stdout.decode().split()
            if historial:
                errores.append(f"{f['archivo']} ({f['motivo']}) aparece en el historial de git: {historial}; "
                               "hay que limpiarlo antes de subir")


CAMPOS_CATALOGO = ["capa", "tabla", "id_fuente", "formato", "archivo_csv", "clave", "granularidad",
                   "cobertura_inicio", "cobertura_fin", "territorio", "unidad", "fuente", "version_fuente",
                   "filas", "responsable"]


def regla_catalogo() -> None:
    if not (RAIZ / "catalogo_tablas.csv").exists():
        errores.append("falta catalogo_tablas.csv (catálogo de tablas curadas)")
        return
    catalogo = leer_csv("catalogo_tablas.csv")
    if not catalogo:
        errores.append("catalogo_tablas.csv está vacío")
        return
    faltan = [c for c in CAMPOS_CATALOGO if c not in catalogo[0]]
    if faltan:
        errores.append(f"catalogo_tablas.csv no tiene las columnas {faltan}")
        return
    diccionario = leer_csv("diccionario_columnas.csv") if (RAIZ / "diccionario_columnas.csv").exists() else None
    if diccionario is None:
        errores.append("falta diccionario_columnas.csv")
    documentadas = {(d.get("tabla"), d.get("columna")) for d in diccionario or []
                    if d.get("descripcion") and d.get("unidad")}
    for t in catalogo:
        vacios = [c for c in CAMPOS_CATALOGO if not t.get(c)]
        if vacios:
            errores.append(f"catálogo: {t.get('tabla')} sin {vacios}")
        if (t.get("capa") == "simulado" or t.get("id_fuente", "").endswith("-SIM")
                or "SIMULADO_" in t.get("archivo_csv", "")):
            errores.append(f"catálogo: {t.get('tabla')} es simulada; la entrega no lleva datos simulados")
        ruta = dentro_de_raiz(t["archivo_csv"])
        if ruta is None or not ruta.exists():
            errores.append(f"catálogo: no existe {t['archivo_csv']}")
            continue
        with open(ruta, encoding="utf-8", newline="") as f:
            lector = csv.reader(f)
            columnas = next(lector, [])
            # Cuenta registros, no líneas: un campo entrecomillado puede traer saltos de línea.
            filas = sum(1 for _ in lector)
        if str(filas) != t["filas"]:
            errores.append(f"catálogo: {t['tabla']} dice {t['filas']} filas y el archivo tiene {filas}")
        for c in t["clave"].split(";"):
            if c not in columnas:
                errores.append(f"catálogo: la clave {c} no es columna de {t['tabla']}")
        if diccionario is not None:
            sin_doc = [c for c in columnas if (t["tabla"], c) not in documentadas]
            if sin_doc:
                errores.append(f"diccionario: {t['tabla']} tiene {len(sin_doc)} columnas sin descripción o unidad "
                               f"({', '.join(sin_doc[:5])})")


def regla_conciliacion() -> None:
    ruta = RAIZ / "reportes" / "conciliacion.csv"
    if not ruta.exists():
        errores.append("falta reportes/conciliacion.csv")
        return
    for c in leer_csv("reportes/conciliacion.csv"):
        if c.get("cuadra_para_etl_curado") != "True" or c.get("cuadra_original_para_etl") == "False":
            errores.append(f"conciliación: los conteos de {c.get('tabla')} no cuadran ({c.get('nota', '')})")
        if c.get("capa") == "silver" and not (RAIZ / "datos" / "rechazados" / f"{c['tabla']}.csv").exists():
            errores.append(f"falta datos/rechazados/{c['tabla']}.csv")


def regla_carpetas() -> None:
    for base in [RAIZ / "datos" / "originales", RAIZ / "datos" / "para-etl", RAIZ / "campo"]:
        if not base.exists():
            continue
        for tipo in base.iterdir():
            if not tipo.is_dir():
                continue
            n_tipo = tipo.name.split("_", 1)[0]
            for fuente in tipo.iterdir():
                if fuente.is_dir() and re.match(r"^\d+\.\d+_", fuente.name):
                    if int(fuente.name.split(".", 1)[0]) != int(n_tipo):
                        errores.append(f"carpeta con número cruzado: {fuente.relative_to(RAIZ)}")


def main() -> int:
    global RAIZ, EQUIPO
    parser = argparse.ArgumentParser(description="Valida una entrega de fuentes contra las reglas de aceptación.")
    parser.add_argument("--raiz", type=Path, default=RAIZ, help="carpeta raíz de la entrega (repo del equipo)")
    parser.add_argument("--equipo", default="", help="prefijo del equipo, p. ej. E5; si se omite, se toma de fuentes.csv")
    args = parser.parse_args()
    RAIZ = args.raiz.resolve()
    EQUIPO = args.equipo
    if not EQUIPO and (RAIZ / "fuentes.csv").exists():
        primera = next(iter(leer_csv("fuentes.csv")), {})
        EQUIPO = primera.get("id", "").split("-")[0]
    if not EQUIPO:
        print("ERROR: no se pudo saber el equipo; usa --equipo")
        return 1
    print(f"Entrega {EQUIPO} en {RAIZ}")
    fuentes = regla_fuentes()
    regla_manifest(fuentes)
    versionados = archivos_versionados()
    regla_rutas_locales(versionados)
    regla_datos_personales()
    regla_tamanos(versionados)
    regla_carpetas()
    regla_catalogo()
    regla_conciliacion()
    conteo = {e: sum(1 for f in fuentes if f.get("estado") == e) for e in sorted(ESTADOS)}
    print("Fuentes por estado:", conteo)
    unicos = list(dict.fromkeys(errores))
    errores[:] = unicos
    for a in dict.fromkeys(avisos):
        print("AVISO:", a)
    for e in errores:
        print("ERROR:", e)
    print(f"{len(errores)} error(es), {len(avisos)} aviso(s)")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
