"""Asigna la AGEB urbana (cvegeo_ageb) a puntos con lat y lon.

Usa los polígonos de las AGEB urbanas de Yucatán del Marco Geoestadístico del
INEGI que prepara src/para_etl_01_03_05.py. La prueba de punto en polígono es
la de cruce de rayos, vectorizada con numpy y con filtro previo por el
rectángulo de cada polígono; respeta huecos y polígonos múltiples.

Un punto que no cae en ninguna AGEB urbana (zona rural o fuera de Yucatán)
queda sin clave.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

POLIGONOS = (Path(__file__).resolve().parents[1] / "datos" / "para-etl" / "03_inegi" / "3.3_censo_2020_ageb"
             / "ageb_urbana_yucatan_poligonos.geojson")


def _dentro(lon: np.ndarray, lat: np.ndarray, anillo: np.ndarray) -> np.ndarray:
    x, y = anillo[:, 0], anillo[:, 1]
    x2, y2 = np.roll(x, -1), np.roll(y, -1)
    dentro = np.zeros(len(lon), dtype=bool)
    for xa, ya, xb, yb in zip(x, y, x2, y2):
        cruza = (ya > lat) != (yb > lat)
        if cruza.any():
            xc = xa + (lat - ya) * (xb - xa) / np.where(yb != ya, yb - ya, 1e-30)
            dentro ^= cruza & (lon < xc)
    return dentro


class Agebs:
    def __init__(self, ruta: Path = POLIGONOS):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        self.claves, self.partes = [], []
        for r in datos["features"]:
            poligonos = r["geometry"]["coordinates"]
            if r["geometry"]["type"] == "Polygon":
                poligonos = [poligonos]
            anillos = [[np.asarray(a, dtype=float) for a in pol] for pol in poligonos]
            todos = np.concatenate([a[0] for a in anillos])
            caja = (todos[:, 0].min(), todos[:, 0].max(), todos[:, 1].min(), todos[:, 1].max())
            self.claves.append(r["properties"]["cvegeo_ageb"])
            self.partes.append((caja, anillos))

    def asignar(self, lat, lon) -> np.ndarray:
        """Devuelve un arreglo con la cvegeo_ageb de cada punto, o None si no cae en ninguna."""
        lat = np.asarray(lat, dtype=float)
        lon = np.asarray(lon, dtype=float)
        salida = np.full(len(lat), None, dtype=object)
        validos = ~(np.isnan(lat) | np.isnan(lon))
        for clave, ((x0, x1, y0, y1), anillos) in zip(self.claves, self.partes):
            cand = np.flatnonzero(validos & (lon >= x0) & (lon <= x1) & (lat >= y0) & (lat <= y1)
                                  & (salida == None))  # noqa: E711
            if not len(cand):
                continue
            dentro = np.zeros(len(cand), dtype=bool)
            for exterior, *huecos in anillos:
                en_pol = _dentro(lon[cand], lat[cand], exterior)
                for h in huecos:
                    en_pol &= ~_dentro(lon[cand], lat[cand], h)
                dentro |= en_pol
            salida[cand[dentro]] = clave
        return salida
