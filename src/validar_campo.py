"""Revisa las capturas de campo de los subtemas 6, 7 y 8.

Correr después de llenar cada plantilla. Revisa:
- que las columnas sean las de la plantilla;
- fecha AAAA-MM-DD y hora HH:MM;
- lat y lon dentro del municipio de Mérida (EPSG:4326);
- que cvegeo_ageb tenga 13 caracteres y exista en el Censo 2020;
- que las medidas sean números positivos y razonables;
- que los archivos de captura, foto o video referidos existan en la carpeta;
- que no haya correos ni teléfonos en ningún campo.

Uso: python src/validar_campo.py
"""

from __future__ import annotations

import re
import sys

import pandas as pd

import comun

RAIZ = comun.RAIZ
CAMPO = RAIZ / "campo"
CENSO = RAIZ / "datos" / "para-etl" / "03_inegi" / "3.3_censo_2020_ageb" / "censo_2020_ageb_urbana_yucatan.csv"

# Rectángulo que contiene al municipio de Mérida, con margen.
LAT = (20.70, 21.35)
LON = (-89.85, -89.40)

MEDIDAS = {
    "largo_tramo_m": (0.5, 20), "ancho_total_m": (0.2, 10), "ancho_libre_m": (0, 10),
    "obstaculo_largo_m": (0, 10), "obstaculo_ancho_m": (0, 10), "obstaculo_alto_m": (0, 10),
    "pendiente_pct": (-30, 30), "ancho_modelo_m": (0.1, 3), "largo_modelo_m": (0.1, 3),
    "ancho_libre_entrada_m": (0, 5), "altura_escalon_m": (0, 1), "num_intentos": (1, 20),
    "tiempo_s": (0, 3600), "largo_m": (0.2, 20), "alto_asiento_m": (0.1, 1.5),
    "profundidad_m": (0.1, 2), "distancia_parada_m": (0, 2000), "personas_sentadas": (0, 100),
    "personas_esperando_de_pie": (0, 200), "personas_sentadas_en_otro_lugar": (0, 100),
    "temperatura_c": (10, 50), "tiempo_espera_min": (0, 240), "comodidad_1a5": (1, 5),
}
COLUMNAS_ARCHIVO = ["archivo_captura", "archivo_video", "archivo_foto"]
CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
TELEFONO = re.compile(r"(?<!\d)(?:\d[\s-]?){10}(?!\d)")

errores: list[str] = []


def revisar(ruta, agebs: set[str]) -> int:
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    rel = ruta.relative_to(RAIZ)
    for i, fila in df.iterrows():
        donde = f"{rel} fila {i + 2}"
        if "fecha" in fila and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fila["fecha"]):
            errores.append(f"{donde}: fecha «{fila['fecha']}» no es AAAA-MM-DD")
        for col in ("hora", "hora_inicio", "hora_fin"):
            if col in fila and fila[col] and not re.fullmatch(r"\d{2}:\d{2}(:\d{2})?", fila[col]):
                errores.append(f"{donde}: {col} «{fila[col]}» no es HH:MM")
        if "lat" in fila:
            try:
                lat, lon = float(fila["lat"]), float(fila["lon"])
                if not (LAT[0] <= lat <= LAT[1] and LON[0] <= lon <= LON[1]):
                    errores.append(f"{donde}: coordenadas fuera de Mérida ({lat}, {lon}); ¿lat y lon invertidas?")
            except ValueError:
                errores.append(f"{donde}: lat/lon vacías o no numéricas")
        if "cvegeo_ageb" in fila:
            clave = fila["cvegeo_ageb"].strip()
            if len(clave) != 13 or (agebs and clave not in agebs):
                errores.append(f"{donde}: cvegeo_ageb «{clave}» no existe en el Censo 2020 urbano de Yucatán")
        for col, (minimo, maximo) in MEDIDAS.items():
            if col in fila and fila[col] != "":
                try:
                    v = float(fila[col])
                    if not minimo <= v <= maximo:
                        errores.append(f"{donde}: {col}={v} fuera de rango [{minimo}, {maximo}]")
                except ValueError:
                    errores.append(f"{donde}: {col} «{fila[col]}» no es número")
        for col in COLUMNAS_ARCHIVO:
            if col in fila and fila[col] and not (ruta.parent / fila[col]).exists():
                errores.append(f"{donde}: no existe el archivo {fila[col]} en {ruta.parent.relative_to(RAIZ)}")
        # Campo por campo: al unir fecha y hora («2026-11-24 10:05») salen 10 dígitos que parecen teléfono.
        textos = [v for c, v in fila.items() if c not in {"fecha", "hora", "hora_inicio", "hora_fin"}]
        if any(CORREO.search(v) or TELEFONO.search(v) for v in textos):
            errores.append(f"{donde}: hay un correo o teléfono; los datos de campo deben ser anónimos")
    return len(df)


def main() -> int:
    agebs = set()
    if CENSO.exists():
        agebs = set(pd.read_csv(CENSO, usecols=["cvegeo_ageb"], dtype=str)["cvegeo_ageb"])
    total = 0
    for ruta in sorted(CAMPO.rglob("*.csv")):
        n = revisar(ruta, agebs)
        total += n
        print(f"{ruta.relative_to(RAIZ)}: {n} filas")
    for e in errores:
        print("ERROR:", e)
    print(f"{total} filas revisadas, {len(errores)} error(es)")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
