"""GTFS oficial del Sistema Va-y-Ven de la Agencia de Transporte de Yucatán (ATY).

La ATY publica su red (paradas, rutas, trazos, horarios y tarifas) en formato
GTFS. El enlace «GTFS» del menú de transporteyucatan.org.mx apunta al
exportador del productor del feed; el catálogo Mobility Database lo registra
como fuente oficial (mdb-3650) y guarda una copia idéntica.

Lo usan dos fuentes:
- 4.3 Paraderos de transporte público (sustituto de la capa del Geoportal).
- 5.2 ATY, ruta R901 IE-TRAM La Plancha – Teya.

El zip se guarda una sola vez en la carpeta de 4.3 y la 5.2 lo lee de ahí.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

import comun

TIPO = "04_geoportal_merida"
CARPETA = "4.3_paraderos"
NOMBRE_ZIP = "gtfs_va_y_ven_aty.zip"
URL_PRODUCTOR = "https://transit-scheduler.com/api/export-gtfs/latest"
URL_ESPEJO = "https://files.mobilitydatabase.org/mdb-3650/latest.zip"
NOTA = ("GTFS oficial del Sistema Va-y-Ven publicado por la Agencia de Transporte de "
        "Yucatán (agency_id MID). Enlace «GTFS» del menú de https://transporteyucatan.org.mx/ ; "
        "registrado como oficial en Mobility Database (mdb-3650), espejo: " + URL_ESPEJO)


def ruta_zip() -> Path:
    return comun.carpeta_fuente(TIPO, CARPETA) / NOMBRE_ZIP


def asegurar_zip(ficha: dict) -> Path:
    """Baja el GTFS si no existe; primero del productor y, si falla, del espejo."""
    carpeta = comun.carpeta_fuente(TIPO, CARPETA)
    try:
        return comun.descargar(URL_PRODUCTOR, carpeta, NOMBRE_ZIP, ficha, nota=NOTA)
    except requests.RequestException:
        return comun.descargar(URL_ESPEJO, carpeta, NOMBRE_ZIP, ficha, nota=NOTA)


def leer(tabla: str, **kwargs) -> pd.DataFrame:
    """Lee una tabla del GTFS (por ejemplo «stops») como texto."""
    with zipfile.ZipFile(ruta_zip()) as z:
        with z.open(f"{tabla}.txt") as f:
            return pd.read_csv(io.TextIOWrapper(f, encoding="utf-8-sig"), dtype=str, **kwargs)


def leer_filtrado(tabla: str, columna: str, valores: set, bloque: int = 500_000) -> pd.DataFrame:
    """Lee una tabla grande por bloques y conserva solo las filas con columna en valores."""
    with zipfile.ZipFile(ruta_zip()) as z:
        with z.open(f"{tabla}.txt") as f:
            lector = pd.read_csv(io.TextIOWrapper(f, encoding="utf-8-sig"), dtype=str, chunksize=bloque)
            return pd.concat([p[p[columna].isin(valores)] for p in lector], ignore_index=True)


def feed_info() -> dict:
    return leer("feed_info").iloc[0].to_dict()
