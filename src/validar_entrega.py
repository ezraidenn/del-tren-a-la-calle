"""Revisa que la entrega cumpla las reglas de aceptación del servidor.

Reglas:
1. fuentes.csv tiene exactamente 27 filas, ids E8-01.1 a E8-09.3, columnas
   completas y un estado válido (real, derivado, simulado, pendiente).
2. Cada archivo de manifest.csv existe y su SHA-256 coincide.
3. Toda fuente con estado real o derivado tiene archivos en el manifiesto.
4. Ningún archivo con estado real vive en una carpeta de simulados.
5. No hay rutas locales de Windows (carpeta Users de una unidad) ni URL de
   archivo local en los textos del repositorio.
6. Los datos propios de campo/ no traen correos, teléfonos ni CURP.
7. Archivos de más de 50 MB y páginas crudas con datos personales o derechos
   reservados: declarados en externos.csv con motivo y sha256, fuera de git
   y sin rastro en el historial.
8. Las carpetas NN_tipo/N.M_fuente usan el mismo número de subtema.

Termina con código 1 si hay errores.

Uso: python src/validar_entrega.py
"""

from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

import comun

RAIZ = comun.RAIZ
ESTADOS = {"real", "derivado", "simulado", "pendiente"}
COLUMNAS = ["id", "subtema", "tipo_fuente", "nombre", "url_original", "licencia",
            "fecha_descarga", "estado", "carpeta"]
LIMITE_MB = 50

errores: list[str] = []
avisos: list[str] = []


def leer_csv(nombre: str) -> list[dict]:
    with open(RAIZ / nombre, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def regla_fuentes() -> list[dict]:
    filas = leer_csv("fuentes.csv")
    if len(filas) != 27:
        errores.append(f"fuentes.csv tiene {len(filas)} filas; deben ser 27")
    esperados = {f"E8-{s:02d}.{n}" for s in range(1, 10) for n in range(1, 4)}
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
        ruta = RAIZ / f["archivo"]
        for ident in f["id_fuente"].split(";"):
            con_archivos.add(ident)
        if not ruta.exists():
            if f["archivo"] in externos:
                avisos.append(f"externo no presente en local: {f['archivo']}")
            else:
                errores.append(f"manifest: no existe {f['archivo']}")
            continue
        if comun.sha256_de(ruta) != f["sha256"]:
            errores.append(f"manifest: el hash no coincide en {f['archivo']} (corre generar_manifest.py)")
        if f["capa"] == "original" and not f["url"]:
            errores.append(f"manifest: original sin URL {f['archivo']}")
        if "simulad" in f["archivo"].lower() or "SIMULADO_" in f["archivo"]:
            ident = f["id_fuente"]
            if any(x["id"] == ident and x["estado"] == "real" for x in fuentes):
                errores.append(f"{ident}: marcada real pero tiene archivos simulados ({f['archivo']})")
    for x in fuentes:
        if x["estado"] in {"real", "derivado"} and x["id"] not in con_archivos:
            errores.append(f"{x['id']}: estado {x['estado']} sin archivos en manifest.csv")


def archivos_versionados() -> list[str]:
    salida = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ, capture_output=True, check=True)
    return [p for p in salida.stdout.decode("utf-8").split("\0") if p]


def regla_rutas_locales(versionados: list[str]) -> None:
    patron = re.compile(r"[A-Za-z]:\\Users\\|file:/{3}")
    for rel in versionados:
        if rel.startswith("datos/originales/") or not rel.endswith((".md", ".py", ".csv", ".json", ".txt", ".sql")):
            continue
        ruta = RAIZ / rel
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
        ruta = RAIZ / rel
        if ruta.exists() and ruta.stat().st_size > LIMITE_MB * 1024 * 1024:
            errores.append(f"archivo de más de {LIMITE_MB} MB versionado en git: {rel}")
    for rel in externos:
        if rel in versionados:
            errores.append(f"externo versionado en git: {rel}")
    for f in leer_csv("externos.csv"):
        if not f.get("motivo") or len(f.get("sha256", "")) != 64:
            errores.append(f"externos.csv: falta motivo o sha256 en {f['archivo']}")
        if f.get("motivo") in {"privacidad", "derechos"}:
            historial = subprocess.run(["git", "log", "--all", "--format=%h", "--", f["archivo"]],
                                       cwd=RAIZ, capture_output=True, text=True).stdout.split()
            if historial:
                errores.append(f"{f['archivo']} ({f['motivo']}) aparece en el historial de git: {historial}; "
                               "hay que limpiarlo antes de subir")


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
    fuentes = regla_fuentes()
    regla_manifest(fuentes)
    versionados = archivos_versionados()
    regla_rutas_locales(versionados)
    regla_datos_personales()
    regla_tamanos(versionados)
    regla_carpetas()
    conteo = {e: sum(1 for f in fuentes if f["estado"] == e) for e in sorted(ESTADOS)}
    print("Fuentes por estado:", conteo)
    for a in avisos:
        print("AVISO:", a)
    for e in errores:
        print("ERROR:", e)
    print(f"{len(errores)} error(es), {len(avisos)} aviso(s)")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
