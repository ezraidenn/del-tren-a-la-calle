"""Prepara para el ETL las fuentes de los subtemas 1, 3.3 y 5.1.

Lee los originales sin modificarlos y escribe CSV UTF-8 en datos/para-etl/ con:
- nombres de columna en minúsculas;
- claves geográficas del INEGI como texto con ceros a la izquierda:
  cvegeo_mun (5), cvegeo_loc (9) y cvegeo_ageb (13);
- coordenadas en grados decimales, EPSG:4326, en columnas lat y lon;
- valores reservados del Censo («*», «N/D») como vacíos.

Uso: python src/para_etl_01_03_05.py
"""

from __future__ import annotations

import io
import json
import re
import zipfile

import pandas as pd

import comun

MESES = {m: i for i, m in enumerate(
    ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
     "septiembre", "octubre", "noviembre", "diciembre"], start=1)}


def leer_json(tipo: str, fuente: str, archivo: str) -> pd.DataFrame:
    ruta = comun.ORIGINALES / tipo / fuente / archivo
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    df = pd.DataFrame(datos["records"]).drop(columns=["_id"], errors="ignore")
    # Si la fuente trae la misma columna en mayúsculas y en minúsculas
    # (p. ej. LATITUD en grados y minutos y latitud decimal), la de mayúsculas
    # se conserva con el sufijo _texto.
    originales = list(df.columns)
    nuevos = []
    for c in originales:
        n = c.lower().replace(".", "_")
        if c != n and n in originales:
            n += "_texto"
        nuevos.append(n)
    df.columns = nuevos
    return df


def escribir(df: pd.DataFrame, tipo: str, fuente: str, archivo: str) -> None:
    carpeta = comun.carpeta_fuente(tipo, fuente, base=comun.PARA_ETL)
    df.to_csv(carpeta / archivo, index=False, encoding="utf-8", lineterminator="\n")
    print(f"  {tipo}/{fuente}/{archivo}: {len(df):,} filas, {len(df.columns)} columnas")


def dms_a_decimal(texto: str | None) -> float | None:
    """Convierte «89°40'51.191\" W» a grados decimales con signo."""
    if not isinstance(texto, str):
        return None
    m = re.match(r"\s*(\d+)\D+(\d+)\D+([\d.]+)\D*([NSEW])", texto)
    if not m:
        return None
    g, mi, s, h = m.groups()
    valor = int(g) + int(mi) / 60 + float(s) / 3600
    return -valor if h in "SW" else valor


def subtema_1() -> None:
    print("Subtema 1")
    t = "01_datos_gob"
    imm = leer_json(t, "1.1_conapo_marginacion", "imm_2020_municipal_5_estados.json")
    imm.insert(0, "cvegeo_mun", imm["cve_mun"].astype(int).astype(str).str.zfill(5))
    escribir(imm, t, "1.1_conapo_marginacion", "marginacion_municipal_2020.csv")

    imu = leer_json(t, "1.1_conapo_marginacion", "imu_2020_ageb_yucatan.json")
    imu.insert(0, "cvegeo_ageb", imu["cve_ageb"].astype(str).str.zfill(13))
    imu.insert(1, "cvegeo_mun", imu["cvegeo_ageb"].str[:5])
    escribir(imu, t, "1.1_conapo_marginacion", "marginacion_urbana_ageb_yucatan_2020.csv")

    for archivo, salida in [("pobproy_quinq_municipal_5_estados.json", "poblacion_quinquenal_municipal.csv"),
                            ("pobproy_inddemo_municipal_5_estados.json", "indicadores_demograficos_municipal.csv")]:
        df = leer_json(t, "1.2_conapo_proyecciones", archivo)
        df.insert(0, "cvegeo_mun", df["clave"].astype(str).str.zfill(5))
        df["ano"] = df["ano"].astype(int)
        escribir(df, t, "1.2_conapo_proyecciones", salida)

    acu = leer_json(t, "1.3_conapo_accesibilidad", "acu_municipal_5_estados.json")
    acu.insert(0, "cvegeo_mun", acu["cve_geo"].astype(str).str.zfill(5))
    escribir(acu, t, "1.3_conapo_accesibilidad", "accesibilidad_municipal.csv")

    loc = leer_json(t, "1.3_conapo_accesibilidad", "acu_localidad_yucatan.json")
    loc.insert(0, "cvegeo_loc", loc["cve_geo"].astype(str).str.zfill(9))
    loc.insert(1, "cvegeo_mun", loc["cvegeo_loc"].str[:5])
    loc.insert(2, "lat", pd.to_numeric(loc["latitud"], errors="coerce").round(6))
    loc.insert(3, "lon", pd.to_numeric(loc["longitud"], errors="coerce").round(6))
    # Respaldo: si falta el decimal, se calcula desde grados y minutos.
    loc["lat"] = loc["lat"].fillna(loc["latitud_texto"].map(dms_a_decimal))
    loc["lon"] = loc["lon"].fillna(loc["longitud_texto"].map(dms_a_decimal))
    escribir(loc, t, "1.3_conapo_accesibilidad", "accesibilidad_localidad_yucatan.csv")


def subtema_3() -> None:
    print("Subtema 3.3")
    zip_ruta = comun.ORIGINALES / "03_inegi" / "3.3_censo_2020_ageb" / "ageb_mza_urbana_31_cpv2020_csv.zip"
    with zipfile.ZipFile(zip_ruta) as z:
        nombre = next(n for n in z.namelist() if n.endswith(".csv") and "conjunto_de_datos" in n)
        with z.open(nombre) as f:
            df = pd.read_csv(io.TextIOWrapper(f, encoding="utf-8-sig"), dtype=str, na_values=["*", "N/D"],
                             keep_default_na=True)
    df.columns = [c.lower() for c in df.columns]
    # Renglones de total por AGEB: manzana 000 y AGEB distinta de 0000.
    ageb = df[(df["mza"] == "000") & (df["ageb"] != "0000")].copy()
    ageb.insert(0, "cvegeo_ageb", ageb["entidad"].str.zfill(2) + ageb["mun"].str.zfill(3)
                + ageb["loc"].str.zfill(4) + ageb["ageb"].str.zfill(4))
    ageb.insert(1, "cvegeo_mun", ageb["cvegeo_ageb"].str[:5])
    textos = {"entidad", "nom_ent", "mun", "nom_mun", "loc", "nom_loc", "ageb", "mza", "cvegeo_ageb", "cvegeo_mun"}
    for c in ageb.columns.difference(list(textos)):
        ageb[c] = pd.to_numeric(ageb[c], errors="coerce")
    escribir(ageb, "03_inegi", "3.3_censo_2020_ageb", "censo_2020_ageb_urbana_yucatan.csv")


def subtema_5() -> None:
    print("Subtema 5.1")
    t, f = "05_solicitud_datos", "5.1_tren_maya_pasajeros"
    filas = []
    for anio in (2025, 2026):
        p = leer_json(t, f, f"pasajeros_{anio}.json")
        b = leer_json(t, f, f"boletos_{anio}.json")
        k = leer_json(t, f, f"kilometros_{anio}.json")
        for df, col, var in [(p, "cantidad_pasajeros_transportados", "pasajeros_transportados"),
                             (b, "boletos_vendidos_pasajeros", "boletos_vendidos"),
                             (k, "kilometros_recorridos", "kilometros_recorridos")]:
            for _, r in df.iterrows():
                mes = MESES[str(r["mes"]).strip().lower()]
                inicio = pd.Timestamp(int(r["anio"]), mes, 1)
                filas.append({"periodo_inicio": inicio.date(), "periodo_fin": (inicio + pd.offsets.MonthEnd(0)).date(),
                              "variable": var, "valor": r[col], "archivo_origen": f"{var.split('_')[0]}_{anio}.json"})
    p24 = leer_json(t, f, "pasajeros_2024.json")
    for _, r in p24.iterrows():
        filas.append({"periodo_inicio": pd.Timestamp(r["inicio_periodo"]).date(),
                      "periodo_fin": pd.Timestamp(r["fin_periodo"]).date(),
                      "variable": "pasajeros_transportados", "valor": r["cantidad_pasajeros"],
                      "archivo_origen": "pasajeros_2024.json"})
    b24 = leer_json(t, f, "boletos_2024.json")
    for _, r in b24.iterrows():
        for col, var in [("boletos_vendidos_estaciones", "boletos_vendidos_estaciones"),
                         ("boletos_vendidos_puntos_venta", "boletos_vendidos_puntos_venta")]:
            filas.append({"periodo_inicio": pd.Timestamp(r["inicio"]).date(), "periodo_fin": pd.Timestamp(r["fin"]).date(),
                          "variable": var, "valor": r[col], "archivo_origen": "boletos_2024.json"})
    df = pd.DataFrame(filas).sort_values(["variable", "periodo_inicio"]).reset_index(drop=True)
    df.insert(0, "territorio", "Red completa del Tren Maya")
    escribir(df, t, f, "servicio_tren_maya_mensual.csv")


if __name__ == "__main__":
    subtema_1()
    subtema_3()
    subtema_5()
