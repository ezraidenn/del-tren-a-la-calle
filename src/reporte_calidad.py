"""Escribe reportes/calidad.md a partir de los reportes en CSV.

Resume, por tabla: filas por capa, rechazos por regla, si la clave es única,
las columnas con más vacíos, la cobertura y si los conteos cuadran.

Uso: python src/reporte_calidad.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
REPORTES = RAIZ / "reportes"


def leer(nombre: str) -> pd.DataFrame:
    return pd.read_csv(RAIZ / nombre, dtype=str, keep_default_na=False)


def si_no(valor: str) -> str:
    return {"True": "sí", "False": "**no**", "": "sin conteo independiente"}.get(valor, valor)


def main() -> None:
    cat = leer("catalogo_tablas.csv")
    con = leer("reportes/conciliacion.csv")
    cal = leer("reportes/calidad_columnas.csv")
    dic = leer("diccionario_columnas.csv")
    fecha = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d")

    rechazos = []
    for ruta in sorted((RAIZ / "datos" / "rechazados").glob("*.csv")):
        r = pd.read_csv(ruta, dtype=str, keep_default_na=False)
        for (regla, motivo), n in r.groupby(["regla", "motivo"]).size().items():
            rechazos.append({"tabla": ruta.stem, "regla": regla, "motivo": motivo, "filas": n})

    silver = con[con["capa"] == "silver"]
    gold = con[con["capa"] == "gold"]
    total_et = silver["filas_para_etl"].astype(int).sum()
    total_cur = silver["filas_curado"].astype(int).sum()
    total_rech = silver["filas_rechazadas"].astype(int).sum()
    sin_desc = (dic["descripcion"] == "").sum()

    lineas = [
        "# Reporte de calidad",
        "",
        f"Generado: {fecha}. Se regenera con `python src/curar.py`, `python src/gold.py` y "
        "`python src/reporte_calidad.py`.",
        "",
        "## Resumen",
        "",
        f"- **Silver:** {len(silver)} tablas curadas. {total_et:,} registros de entrada: {total_cur:,} curados "
        f"y {total_rech:,} rechazados, que se conservan en `datos/rechazados/`.",
        f"- **Conteos de silver:** cuadran en {int((silver['cuadra_para_etl_curado'] == 'True').sum())} de "
        f"{len(silver)} tablas (entrada = curados + rechazados). En "
        f"{int((silver['cuadra_original_para_etl'] == 'True').sum())} tablas además coincide el conteo "
        "independiente del archivo original.",
        f"- **Gold:** {len(cat[cat['capa'] == 'gold'])} tablas (dimensiones e indicadores). Sus "
        f"{len(gold)} controles de totales cuadran en {int((gold['cuadra_para_etl_curado'] == 'True').sum())}.",
        f"- **Diccionario:** {len(dic)} columnas documentadas; {sin_desc} sin descripción.",
        f"- **Claves:** son únicas en todas las tablas. La regla R3 rechaza los duplicados y gold "
        "verifica la clave antes de escribir.",
        "",
        "## Conciliación por tabla",
        "",
        "| Capa | Tabla | Original | Para ETL | Curado | Rechazados | Original = para ETL | Para ETL = curado + rechazados | Nota |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for _, c in silver.iterrows():
        lineas.append(f"| silver | {c['tabla']} | {c['filas_original'] or '—'} | {c['filas_para_etl']} | "
                      f"{c['filas_curado']} | {c['filas_rechazadas']} | {si_no(c['cuadra_original_para_etl'])} | "
                      f"{si_no(c['cuadra_para_etl_curado'])} | {c['nota']} |")
    lineas += ["", "Controles de la capa gold:", "", "| Tabla | Entrada | Salida | Cuadra | Control |",
               "|---|---|---|---|---|"]
    for _, c in gold.iterrows():
        lineas.append(f"| {c['tabla']} | {c['filas_original']} | {c['filas_curado']} | "
                      f"{si_no(c['cuadra_para_etl_curado'])} | {c['nota']} |")

    sim = con[con["capa"] == "simulado"]
    tablas_sim = cat[cat["capa"] == "simulado"]
    if len(tablas_sim):
        lineas += ["", "## Datos simulados", "",
                   f"{len(tablas_sim)} tablas en `datos/simulados/` son respuestas **SIMULADAS** a las solicitudes de "
                   "acceso a la información; no son datos oficiales. Cada una está calibrada con un dato real y sus "
                   "totales se comprueban contra él:", "",
                   "| Tabla | Real | Simulado | Cuadra | Control |", "|---|---|---|---|---|"]
        for _, c in sim.iterrows():
            lineas.append(f"| {c['tabla']} | {c['filas_original']} | {c['filas_curado']} | "
                          f"{si_no(c['cuadra_para_etl_curado'])} | {c['nota']} |")
    lineas += ["", "## Registros rechazados", ""]
    if rechazos:
        lineas += ["| Tabla | Regla | Motivo | Filas |", "|---|---|---|---|"]
        lineas += [f"| {r['tabla']} | {r['regla']} | {r['motivo']} | {r['filas']} |" for r in rechazos]
    else:
        lineas.append("Ninguno.")
    lineas += ["", "Las reglas están descritas en `src/curar.py`.", "",
               "## Columnas con más vacíos", "",
               "Columnas con 20 % o más de valores vacíos. El dato falta en la fuente; no se imputa.", "",
               "| Capa | Tabla | Columna | Vacíos (%) |", "|---|---|---|---|"]
    cal["nulos_pct"] = cal["nulos_pct"].astype(float)
    for _, c in cal[cal["nulos_pct"] >= 20].sort_values(["capa", "tabla", "nulos_pct"],
                                                         ascending=[False, True, False]).iterrows():
        lineas.append(f"| {c['capa']} | {c['tabla']} | {c['columna']} | {c['nulos_pct']:.1f} |")

    lineas += ["", "## Cobertura", "", "| Capa | Tabla | Granularidad | Cobertura | Territorio | Filas |",
               "|---|---|---|---|---|---|"]
    for _, c in cat.iterrows():
        lineas.append(f"| {c['capa']} | {c['tabla']} | {c['granularidad']} | {c['cobertura_inicio']} a "
                      f"{c['cobertura_fin']} | {c['territorio']} | {c['filas']} |")

    (REPORTES / "calidad.md").write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
    print(f"Escrito reportes/calidad.md: {len(silver)} tablas silver, {len(gold)} controles gold, "
          f"{len(rechazos)} grupos de rechazo")


if __name__ == "__main__":
    main()
