"""Genera manifest.csv y externos.csv a partir de los archivos del repositorio.

- manifest.csv: una fila por archivo de datos (originales o bronze, para-etl,
  curados o silver, rechazados, gold, campo y salidas del data mart) con
  bytes, SHA-256 y procedencia.
- externos.csv: archivos que no se versionan en git, con el motivo:
  «tamaño» (más de LIMITE_GIT_MB; el servidor los descarga de su URL),
  «privacidad» (páginas crudas con teléfonos o nombres de personas) o
  «derechos» (páginas con todos los derechos reservados). Los dos últimos
  se entregan al servidor por un canal privado y se verifican por su hash.

La URL y la fecha de los originales salen del procedencia.json de cada fuente.

Uso: python src/generar_manifest.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import comun

RAIZ = comun.RAIZ
LIMITE_GIT_MB = 50
CARPETAS = [
    RAIZ / "datos" / "originales",
    RAIZ / "datos" / "para-etl",
    RAIZ / "datos" / "curados",
    RAIZ / "datos" / "rechazados",
    RAIZ / "datos" / "gold",
    RAIZ / "campo",
    RAIZ / "procesamiento" / "03_denue_datamart" / "data",
]
IGNORAR_NOMBRES = {"procedencia.json", "README.md", ".gitkeep"}
IGNORAR_PARTES = {"processed", "raw", "__pycache__"}
# Carpetas que no se publican en git, con su motivo.
NO_PUBLICAR = {
    "datos/originales/09_scraping/9.1_seccion_amarilla_restaurantes/paginas/": "privacidad",
    "datos/originales/09_scraping/9.3_guia_estacion_teya/paginas/": "derechos",
}


def procedencias() -> dict[Path, dict]:
    """Mapa de archivo original -> datos de su procedencia.json."""
    mapa = {}
    for ficha_ruta in (RAIZ / "datos" / "originales").rglob("procedencia.json"):
        ficha = json.loads(ficha_ruta.read_text(encoding="utf-8"))
        for a in ficha.get("archivos", []):
            mapa[(ficha_ruta.parent / a["archivo"]).resolve()] = {**a, "id": ficha.get("id", "")}
    return mapa


def id_fuente(ruta: Path) -> str:
    """Deduce el id E8-NN.M a partir de la carpeta N.M_ de la ruta."""
    for parte in ruta.parts:
        cabeza = parte.split("_", 1)[0]
        if "." in cabeza and cabeza.replace(".", "").isdigit():
            n, m = cabeza.split(".")
            return f"E8-{int(n):02d}.{m}"
    if "03_denue_datamart" in ruta.parts:
        return "E8-03.1;E8-03.2"
    # Archivo común a las 3 fuentes de un subtema de campo (p. ej. el modelo de la silla del subtema 7).
    if ruta.parts[0] == "campo" and len(ruta.parts) > 1 and ruta.parts[1][:2].isdigit():
        n = int(ruta.parts[1][:2])
        return ";".join(f"E8-{n:02d}.{m}" for m in range(1, 4))
    return ""


def main() -> None:
    fichas = procedencias()
    filas, externos = [], []
    for base in CARPETAS:
        if not base.exists():
            continue
        for ruta in sorted(p for p in base.rglob("*") if p.is_file()):
            rel = ruta.relative_to(RAIZ)
            if (ruta.name in IGNORAR_NOMBRES or IGNORAR_PARTES & set(rel.parts)
                    or ruta.suffix in {".parcial", ".md"}):
                continue
            bytes_ = ruta.stat().st_size
            ficha = fichas.get(ruta.resolve(), {})
            if "originales" in rel.parts:
                capa = "original"
                derivado_de = ""
            elif "para-etl" in rel.parts:
                capa = "para-etl"
                derivado_de = str(Path("datos", "originales", *rel.parts[2:-1])).replace("\\", "/")
            elif "curados" in rel.parts:
                capa = "silver"
                derivado_de = str(Path("datos", "para-etl", *rel.parts[2:-1])).replace("\\", "/")
            elif "rechazados" in rel.parts:
                capa = "rechazado"
                derivado_de = "datos/para-etl"
            elif "gold" in rel.parts:
                capa = "gold"
                derivado_de = "datos/curados"
            elif rel.parts[0] == "campo":
                capa = "campo"
                derivado_de = ""
            else:
                capa = "data-mart"
                derivado_de = "datos/originales/03_inegi"
            fila = {
                "archivo": str(rel).replace("\\", "/"),
                "id_fuente": ficha.get("id") or id_fuente(rel),
                "capa": capa,
                "url": ficha.get("url", ""),
                "derivado_de": derivado_de,
                "bytes": bytes_,
                "sha256": comun.sha256_de(ruta),
                "descargado_utc": ficha.get("descargado_utc", ""),
                "nota": ficha.get("nota", ""),
            }
            filas.append(fila)
            motivo = next((m for pref, m in NO_PUBLICAR.items() if fila["archivo"].startswith(pref)), "")
            if bytes_ > LIMITE_GIT_MB * 1024 * 1024:
                motivo = "tamaño"
            if motivo:
                externos.append({**{k: fila[k] for k in ("archivo", "id_fuente", "url", "bytes", "sha256")},
                                 "motivo": motivo})

    columnas = ["archivo", "id_fuente", "capa", "url", "derivado_de", "bytes", "sha256", "descargado_utc", "nota"]
    with open(RAIZ / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columnas, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    with open(RAIZ / "externos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["archivo", "id_fuente", "url", "bytes", "sha256", "motivo"], lineterminator="\n")
        w.writeheader()
        w.writerows(externos)
    total = sum(f["bytes"] for f in filas)
    print(f"manifest.csv: {len(filas)} archivos, {total / 1e6:.1f} MB")
    print(f"externos.csv: {len(externos)} archivos fuera de git")
    actualizar_gitignore(externos)


def actualizar_gitignore(externos: list[dict]) -> None:
    """Reescribe el bloque de archivos externos al final del .gitignore."""
    ruta = RAIZ / ".gitignore"
    marca = "# --- externos.csv (generado por src/generar_manifest.py) ---"
    texto = ruta.read_text(encoding="utf-8") if ruta.exists() else ""
    salto = "\n"
    texto = texto.split(marca)[0].rstrip(salto) + salto * 2 + marca + salto
    texto += "".join(f"/{e['archivo']}{salto}" for e in externos)
    ruta.write_text(texto, encoding="utf-8", newline=salto)


if __name__ == "__main__":
    main()
