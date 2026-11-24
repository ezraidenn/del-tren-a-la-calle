"""Funciones comunes para descargar fuentes y registrar su procedencia.

Cada fuente vive en datos/originales/<NN_tipo>/<N.M_fuente>/ y lleva un
procedencia.json con la URL, los parámetros, la fecha UTC, los bytes y el
SHA-256 de cada archivo descargado. Los archivos de originales/ no se editan.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[1]
ORIGINALES = RAIZ / "datos" / "originales"
PARA_ETL = RAIZ / "datos" / "para-etl"

AGENTE = "del-tren-a-la-calle/1.0 (proyecto escolar UPY; descarga de datos abiertos)"
SESION = requests.Session()
SESION.headers.update({"User-Agent": AGENTE})


def ahora_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def carpeta_fuente(tipo: str, fuente: str, base: Path = ORIGINALES) -> Path:
    carpeta = base / tipo / fuente
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


def leer_procedencia(carpeta: Path) -> dict:
    ruta = carpeta / "procedencia.json"
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    return {}


def guardar_procedencia(carpeta: Path, datos: dict) -> None:
    ruta = carpeta / "procedencia.json"
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def registrar(carpeta: Path, ficha: dict, archivo: dict) -> None:
    """Agrega o reemplaza un archivo en el procedencia.json de la fuente."""
    datos = leer_procedencia(carpeta)
    datos.update({k: v for k, v in ficha.items() if k != "archivos"})
    archivos = [a for a in datos.get("archivos", []) if a["archivo"] != archivo["archivo"]]
    archivos.append(archivo)
    datos["archivos"] = sorted(archivos, key=lambda a: a["archivo"])
    guardar_procedencia(carpeta, datos)


def descargar(url: str, carpeta: Path, nombre: str, ficha: dict, nota: str = "",
              reintentos: int = 3, forzar: bool = False) -> Path:
    """Descarga una URL tal cual y la registra. No vuelve a bajar si ya existe."""
    destino = carpeta / nombre
    if destino.exists() and not forzar:
        print(f"  ya existe {destino.relative_to(RAIZ)}")
        return destino
    for intento in range(1, reintentos + 1):
        try:
            with SESION.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                temporal = destino.with_suffix(destino.suffix + ".parcial")
                with open(temporal, "wb") as f:
                    for bloque in r.iter_content(1 << 20):
                        f.write(bloque)
                temporal.replace(destino)
                tipo = r.headers.get("Content-Type", "")
            break
        except requests.RequestException as e:
            print(f"  intento {intento} falló: {e}")
            if intento == reintentos:
                raise
            time.sleep(5 * intento)
    registrar(carpeta, ficha, {
        "archivo": nombre,
        "url": url,
        "descargado_utc": ahora_utc(),
        "bytes": destino.stat().st_size,
        "sha256": sha256_de(destino),
        "content_type": tipo,
        "nota": nota,
    })
    print(f"  bajado {destino.relative_to(RAIZ)} ({destino.stat().st_size:,} bytes)")
    return destino


def ckan_datastore(resource_id: str, carpeta: Path, nombre: str, ficha: dict,
                   filtros: dict | None = None, pagina: int = 1000, nota: str = "",
                   forzar: bool = False) -> Path:
    """Baja un recurso de datos.gob.mx por la API oficial CKAN DataStore.

    Guarda todas las páginas en un solo JSON con los registros y los campos,
    tal como los devuelve la API.
    """
    destino = carpeta / nombre
    if destino.exists() and not forzar:
        print(f"  ya existe {destino.relative_to(RAIZ)}")
        return destino
    api = "https://www.datos.gob.mx/api/3/action/datastore_search"
    registros, campos, desplazamiento, total = [], None, 0, None
    while True:
        params = {"resource_id": resource_id, "limit": pagina, "offset": desplazamiento}
        if filtros:
            params["filters"] = json.dumps(filtros, ensure_ascii=False)
        r = SESION.get(api, params=params, timeout=120)
        r.raise_for_status()
        res = r.json()["result"]
        campos = campos or res.get("fields")
        total = res.get("total", total)
        lote = res.get("records", [])
        registros.extend(lote)
        desplazamiento += len(lote)
        if not lote or desplazamiento >= (total or 0):
            break
        time.sleep(0.5)
    destino.write_text(json.dumps({"resource_id": resource_id, "filtros": filtros, "total": total,
                                   "fields": campos, "records": registros},
                                  ensure_ascii=False) + "\n", encoding="utf-8")
    registrar(carpeta, ficha, {
        "archivo": nombre,
        "url": api,
        "parametros": {"resource_id": resource_id, "filters": filtros, "limit": pagina},
        "descargado_utc": ahora_utc(),
        "bytes": destino.stat().st_size,
        "sha256": sha256_de(destino),
        "content_type": "application/json",
        "registros": len(registros),
        "nota": nota,
    })
    print(f"  bajado {destino.relative_to(RAIZ)} ({len(registros):,} registros)")
    return destino


def ckan_paquete(dataset: str) -> dict:
    r = SESION.get("https://www.datos.gob.mx/api/3/action/package_show", params={"id": dataset}, timeout=60)
    r.raise_for_status()
    return r.json()["result"]
