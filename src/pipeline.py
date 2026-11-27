"""Corre el pipeline completo del equipo E8 en orden.

Etapas:
1. bronze   : descarga de originales (solo con --descargar; no vuelve a bajar lo que ya existe)
2. para-etl : extracción y limpieza inicial de cada fuente
3. silver   : curado, reglas de calidad, rechazados y conciliación (src/curar.py)
4. gold     : dimensiones e indicadores (src/gold.py)
5. booklet  : datos y páginas del capítulo del booklet (src/booklet.py)
6. control  : reporte de calidad, manifiesto y validación de la entrega

Se detiene en la primera etapa que falle. La carga a PostgreSQL es aparte:
python src/cargar_staging.py

Uso:
    python src/pipeline.py               # de para-etl a control, con los originales del repositorio
    python src/pipeline.py --descargar   # además baja los originales que falten
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

SRC = Path(__file__).resolve().parent

DESCARGAS = [
    "01_05_datos_gob.py", "02_siegy.py", "03_inegi.py", "04_geoportal_merida.py",
    "05_aty_ruta_r901.py", "05_ayuntamiento_banquetas.py",
    "scraping/9.1_seccion_amarilla_restaurantes.py", "scraping/9.2_tren_maya_horarios.py",
    "scraping/9.3_guia_estacion_teya.py",
]
PREPARACION = ["para_etl_01_03_05.py"]
POSTERIORES = ["curar.py", "gold.py", "booklet.py", "reporte_calidad.py", "generar_manifest.py",
               "validar_entrega.py"]


def correr(script: str) -> bool:
    inicio = time.perf_counter()
    print(f"\n=== {script}", flush=True)
    resultado = subprocess.run([sys.executable, str(SRC / script)], cwd=SRC.parent)
    print(f"=== {script}: {'ok' if resultado.returncode == 0 else 'FALLÓ'} en "
          f"{time.perf_counter() - inicio:.1f} s", flush=True)
    return resultado.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline del equipo E8")
    parser.add_argument("--descargar", action="store_true", help="incluye la descarga de originales")
    args = parser.parse_args()
    etapas = (DESCARGAS if args.descargar else []) + PREPARACION + POSTERIORES
    for script in etapas:
        if not correr(script):
            return 1
    print("\nPipeline completo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
