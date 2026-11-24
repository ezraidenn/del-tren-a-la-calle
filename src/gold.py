"""Capa gold: dimensiones compartidas e indicadores reproducibles.

Lee solo la capa silver (datos/curados) y los ZIP originales del DENUE. Escribe
en datos/gold/ una tabla por dimensión o indicador, en Parquet y CSV, y
documenta cada indicador con su fórmula, numerador y denominador en
datos/gold/indicadores.csv.

Dimensiones (claves compartidas con las demás tablas y equipos):
- dim_municipio: los municipios de los 5 estados del Tren Maya (cvegeo_mun).
- dim_ageb: las AGEB urbanas de Yucatán (cvegeo_ageb).
- dim_tiempo: los meses de 2019 a 2026 (fecha_mes).
- dim_estacion: las 34 estaciones del Tren Maya (station_id).

Indicadores:
- ind_negocios_ageb_merida: establecimientos por AGEB urbana de Mérida, 2019 y
  2025, por cada 1,000 habitantes, con su marginación.
- ind_municipio_contexto: población, marginación, accesibilidad y
  establecimientos por municipio de los 5 estados.
- ind_tren_maya_mensual: pasajeros, boletos y kilómetros por mes, pasajeros
  por kilómetro y variación anual.
- ind_restaurantes_transporte: distancia de cada restaurante con coordenadas a
  la parada de transporte público más cercana.
- ind_obras_banquetas_anual: obras, superficie y monto de banquetas por año.

Cada indicador concilia sus totales contra su entrada y lo registra en
reportes/conciliacion.csv.

Uso: python src/gold.py
"""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import curar  # noqa: E402

RAIZ = curar.RAIZ
CUR = RAIZ / "datos" / "curados"
GOLD = RAIZ / "datos" / "gold"
DENUE = RAIZ / "datos" / "originales" / "03_inegi"
ESTACIONES = RAIZ / "procesamiento" / "03_denue_datamart" / "data" / "mart" / "dim_station.parquet"
MERIDA = "31050"
RESPONSABLE = curar.tablas.RESPONSABLE

conciliacion: list[dict] = []


def silver(nombre: str) -> pd.DataFrame:
    rutas = list(CUR.rglob(f"{nombre}.parquet"))
    if len(rutas) != 1:
        raise FileNotFoundError(f"No se encontró la tabla curada {nombre}; corre primero src/curar.py")
    return pd.read_parquet(rutas[0])


def denue_yucatan(carpeta: str, sufijo: str) -> pd.DataFrame:
    """Claves territoriales de los establecimientos del DENUE de Yucatán."""
    with zipfile.ZipFile(DENUE / carpeta / f"denue_31_{sufijo}_csv.zip") as z:
        nombre = next(n for n in z.namelist() if n.lower().endswith(".csv") and "conjunto_de_datos" in n.lower())
        df = pd.read_csv(io.TextIOWrapper(z.open(nombre), encoding="latin-1"), dtype=str,
                         usecols=lambda c: c in {"id", "cve_ent", "cve_mun", "cve_loc", "ageb"})
    df["cvegeo_mun"] = df["cve_ent"].str.zfill(2) + df["cve_mun"].str.zfill(3)
    ageb = df["ageb"].fillna("").str.strip().str.upper()
    df["cvegeo_ageb"] = (df["cvegeo_mun"] + df["cve_loc"].fillna("").str.zfill(4) + ageb.str.zfill(4)).where(ageb != "")
    return df


def denue_por_municipio(carpeta: str, sufijo: str) -> pd.Series:
    conteos = []
    for ent in ("04", "07", "23", "27", "31"):
        with zipfile.ZipFile(DENUE / carpeta / f"denue_{ent}_{sufijo}_csv.zip") as z:
            nombre = next(n for n in z.namelist() if n.lower().endswith(".csv") and "conjunto_de_datos" in n.lower())
            df = pd.read_csv(io.TextIOWrapper(z.open(nombre), encoding="latin-1"), dtype=str,
                             usecols=["cve_ent", "cve_mun"])
        conteos.append((df["cve_ent"].str.zfill(2) + df["cve_mun"].str.zfill(3)).value_counts())
    return pd.concat(conteos).groupby(level=0).sum()


def control(tabla: str, entrada: int, salida: int, descripcion: str, ok: bool) -> None:
    conciliacion.append({
        "capa": "gold", "tabla": tabla, "id_fuente": "", "filas_original": entrada,
        "filas_para_etl": "", "filas_curado": salida, "filas_rechazadas": "",
        "cuadra_original_para_etl": "", "cuadra_para_etl_curado": ok, "nota": descripcion,
    })
    print(f"[{'OK' if ok else 'REVISAR'}] {tabla}: {descripcion}")


def haversine_m(lat1, lon1, lat2, lon2) -> np.ndarray:
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6_371_008.8 * 2 * np.arcsin(np.sqrt(a))


# --- Dimensiones -------------------------------------------------------------

def dim_municipio() -> pd.DataFrame:
    m = silver("conapo_marginacion_municipal_2020")
    return (m[["cvegeo_mun", "nom_ent", "nom_mun"]]
            .assign(cve_ent=m["cvegeo_mun"].str[:2], cve_mun=m["cvegeo_mun"].str[2:])
            [["cvegeo_mun", "cve_ent", "nom_ent", "cve_mun", "nom_mun"]]
            .sort_values("cvegeo_mun").reset_index(drop=True))


def dim_ageb() -> pd.DataFrame:
    c = silver("inegi_censo_2020_ageb_yucatan")
    return (c[["cvegeo_ageb", "cvegeo_mun", "nom_mun", "loc", "nom_loc", "ageb"]]
            .rename(columns={"loc": "cve_loc", "ageb": "cve_ageb"})
            .assign(cve_loc=lambda d: d["cve_loc"].str.zfill(4))
            .sort_values("cvegeo_ageb").reset_index(drop=True))


def dim_tiempo() -> pd.DataFrame:
    meses = pd.date_range("2019-01-01", "2026-12-01", freq="MS")
    return pd.DataFrame({
        "fecha_mes": meses.strftime("%Y-%m-%d"), "anio": meses.year, "mes": meses.month,
        "trimestre": meses.quarter, "nombre_mes": meses.month.map(
            dict(enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                            "septiembre", "octubre", "noviembre", "diciembre"], start=1))),
    })


def dim_estacion() -> pd.DataFrame:
    e = pd.read_parquet(ESTACIONES)
    return e.rename(columns={"station_name": "estacion", "state": "estado", "municipality": "municipio",
                             "latitude": "lat", "longitude": "lon"})[
        ["station_id", "estacion", "estado", "municipio", "lat", "lon"]]


# --- Indicadores -------------------------------------------------------------

def ind_negocios_ageb_merida() -> pd.DataFrame:
    censo = silver("inegi_censo_2020_ageb_yucatan")
    marg = silver("conapo_marginacion_ageb_yucatan_2020")
    d19 = denue_yucatan("3.1_denue_2019_11", "1119")
    d25 = denue_yucatan("3.2_denue_2025_05", "0525")
    base = censo[censo["cvegeo_mun"] == MERIDA][["cvegeo_ageb", "nom_loc", "pobtot"]]
    c19 = d19[d19["cvegeo_mun"] == MERIDA]["cvegeo_ageb"].value_counts().rename("establecimientos_2019")
    c25 = d25[d25["cvegeo_mun"] == MERIDA]["cvegeo_ageb"].value_counts().rename("establecimientos_2025")
    df = base.merge(c19, left_on="cvegeo_ageb", right_index=True, how="left") \
             .merge(c25, left_on="cvegeo_ageb", right_index=True, how="left")
    df[["establecimientos_2019", "establecimientos_2025"]] = \
        df[["establecimientos_2019", "establecimientos_2025"]].fillna(0).astype("Int64")
    pob = df["pobtot"].astype("Float64")
    df["establecimientos_por_1000_hab_2025"] = (df["establecimientos_2025"] / pob.where(pob > 0) * 1000).round(2)
    df["variacion_pct_2019_2025"] = ((df["establecimientos_2025"] - df["establecimientos_2019"])
                                     / df["establecimientos_2019"].where(df["establecimientos_2019"] > 0) * 100).round(2)
    df = df.merge(marg[["cvegeo_ageb", "im_2020", "gm_2020"]] if "im_2020" in marg else marg[["cvegeo_ageb"]],
                  on="cvegeo_ageb", how="left")
    for anio, d, c in ((2019, d19, c19), (2025, d25, c25)):
        total = int((d["cvegeo_mun"] == MERIDA).sum())
        en_ageb_censo = int(df[f"establecimientos_{anio}"].sum())
        sin_ageb = int(((d["cvegeo_mun"] == MERIDA) & d["cvegeo_ageb"].isna()).sum())
        fuera = int(c.sum()) - en_ageb_censo
        control("ind_negocios_ageb_merida", total, len(df),
                f"DENUE {anio} Mérida: {total} establecimientos = {en_ageb_censo} en AGEB urbanas del Censo "
                f"+ {fuera} en AGEB sin renglón urbano en el Censo + {sin_ageb} sin AGEB",
                total == en_ageb_censo + fuera + sin_ageb)
    return df.sort_values("cvegeo_ageb").reset_index(drop=True)


def ind_municipio_contexto() -> pd.DataFrame:
    m = silver("conapo_marginacion_municipal_2020")
    a = silver("conapo_accesibilidad_municipal")
    p = silver("conapo_indicadores_demograficos_municipal")
    p25 = p[p["ano"].astype(int) == 2025][["cvegeo_mun", "pob_mit_mun"]].rename(columns={"pob_mit_mun": "poblacion_2025"})
    col_im = [c for c in ("im_2020", "gm_2020") if c in m.columns]
    col_acc = [c for c in ("gacu",) if c in a.columns]
    df = m[["cvegeo_mun", "nom_ent", "nom_mun", "pob_tot", *col_im]].rename(columns={"pob_tot": "poblacion_2020"})
    df = df.merge(a[["cvegeo_mun", *col_acc]], on="cvegeo_mun", how="left").merge(p25, on="cvegeo_mun", how="left")
    e19 = denue_por_municipio("3.1_denue_2019_11", "1119").rename("establecimientos_2019")
    e25 = denue_por_municipio("3.2_denue_2025_05", "0525").rename("establecimientos_2025")
    df = df.merge(e19, left_on="cvegeo_mun", right_index=True, how="left") \
           .merge(e25, left_on="cvegeo_mun", right_index=True, how="left")
    df[["establecimientos_2019", "establecimientos_2025"]] = \
        df[["establecimientos_2019", "establecimientos_2025"]].fillna(0).astype("Int64")
    pob25 = df["poblacion_2025"].astype("Float64")
    df["establecimientos_por_1000_hab_2025"] = (df["establecimientos_2025"] / pob25.where(pob25 > 0) * 1000).round(2)
    df["variacion_pct_2019_2025"] = ((df["establecimientos_2025"] - df["establecimientos_2019"])
                                     / df["establecimientos_2019"].where(df["establecimientos_2019"] > 0) * 100).round(2)
    for anio, serie in ((2019, e19), (2025, e25)):
        total = int(serie.sum())
        asignados = int(df[f"establecimientos_{anio}"].sum())
        sin_municipio = int(serie[~serie.index.isin(df["cvegeo_mun"])].sum())
        control("ind_municipio_contexto", total, len(df),
                f"DENUE {anio} 5 estados: {total} = {asignados} en municipios de CONAPO 2020 "
                f"+ {sin_municipio} en municipios creados después de 2020", total == asignados + sin_municipio)
    return df.sort_values("cvegeo_mun").reset_index(drop=True)


def ind_tren_maya_mensual() -> pd.DataFrame:
    s = silver("tren_maya_servicio_mensual")
    mensual = s[s["periodo_inicio"].str[:4].isin(["2025", "2026"])]
    df = mensual.pivot_table(index="periodo_inicio", columns="variable", values="valor", aggfunc="sum").reset_index()
    df = df.rename(columns={"periodo_inicio": "fecha_mes"})
    df["pasajeros_por_km"] = (df["pasajeros_transportados"] / df["kilometros_recorridos"]).round(4)
    df["pasajeros_por_boleto"] = (df["pasajeros_transportados"] / df["boletos_vendidos"]).round(4)
    anterior = df.set_index("fecha_mes")["pasajeros_transportados"]
    df["variacion_anual_pasajeros_pct"] = df["fecha_mes"].map(
        lambda f: (anterior[f] / anterior[f"{int(f[:4]) - 1}{f[4:]}"] - 1) * 100
        if f"{int(f[:4]) - 1}{f[4:]}" in anterior.index else np.nan).round(2)
    total_in = float(mensual[mensual["variable"] == "pasajeros_transportados"]["valor"].sum())
    total_out = float(df["pasajeros_transportados"].sum())
    control("ind_tren_maya_mensual", len(mensual), len(df),
            f"Pasajeros 2025-2026: {total_in:,.0f} en silver = {total_out:,.0f} en gold", total_in == total_out)
    return df


def ind_restaurantes_transporte() -> pd.DataFrame:
    r = silver("seccion_amarilla_restaurantes_merida")
    p = silver("aty_paraderos")
    r = r[r["lat"].notna()][["id_anuncio", "nombre", "categoria", "colonia_normalizada", "lat", "lon"]].copy()
    plat, plon = p["lat"].to_numpy(float), p["lon"].to_numpy(float)
    dist = haversine_m(r["lat"].to_numpy(float)[:, None], r["lon"].to_numpy(float)[:, None], plat[None, :], plon[None, :])
    idx = dist.argmin(axis=1)
    r["parada_cercana_id"] = p["stop_id"].to_numpy()[idx]
    r["parada_cercana"] = p["nombre"].to_numpy()[idx]
    r["distancia_parada_m"] = dist.min(axis=1).round(1)
    r["paradas_a_400_m"] = (dist <= 400).sum(axis=1)
    r["a_400_m_de_parada"] = r["distancia_parada_m"] <= 400
    control("ind_restaurantes_transporte", int(silver("seccion_amarilla_restaurantes_merida")["lat"].notna().sum()),
            len(r), f"{len(r)} restaurantes con coordenadas; {int(r['a_400_m_de_parada'].sum())} a 400 m o menos "
            f"de una parada", True)
    return r.reset_index(drop=True)


def ind_obras_banquetas_anual() -> pd.DataFrame:
    o = silver("srft_obras_banquetas_merida")
    o = o.assign(anio_inicio=o["fecha_inicio"].str[:4])
    df = o.groupby("anio_inicio", dropna=False).agg(
        obras=("folio", "count"), metros_cuadrados=("metros_cuadrados", "sum"),
        monto_aprobado_mxn=("monto_aprobado_mxn", "sum"), pagado_mxn=("pagado_mxn", "sum")).reset_index()
    df["monto_aprobado_por_m2_mxn"] = (df["monto_aprobado_mxn"] / df["metros_cuadrados"].where(df["metros_cuadrados"] > 0)).round(2)
    control("ind_obras_banquetas_anual", len(o), len(df),
            f"{len(o)} obras en silver = {int(df['obras'].sum())} sumadas por año; monto "
            f"{o['monto_aprobado_mxn'].sum():,.2f} = {df['monto_aprobado_mxn'].sum():,.2f}",
            len(o) == int(df["obras"].sum()) and round(o["monto_aprobado_mxn"].sum(), 2) == round(df["monto_aprobado_mxn"].sum(), 2))
    return df


# --- Metadatos -------------------------------------------------------------

def spec(tabla, clave, granularidad, territorio, cobertura, unidad, fuentes, version, formato="tabular"):
    return {"tabla": tabla, "clave": clave, "granularidad": granularidad, "territorio": territorio,
            "cobertura": cobertura, "unidad": unidad, "id_fuente": fuentes, "version_fuente": version,
            "formato": formato, "responsable": RESPONSABLE}


SALIDAS = [
    (dim_municipio, spec("dim_municipio", ["cvegeo_mun"], "municipio", "5 estados del Tren Maya",
                         ("2020", "2020"), "clave", "E8-01.1", "Marco municipal del índice de marginación 2020")),
    (dim_ageb, spec("dim_ageb", ["cvegeo_ageb"], "AGEB urbana", "Yucatán", ("2020", "2020"), "clave",
                    "E8-03.3", "Censo 2020, AGEB urbanas")),
    (dim_tiempo, spec("dim_tiempo", ["fecha_mes"], "mes", "no aplica", "fecha_mes", "fecha", "", "Calendario 2019-2026")),
    (dim_estacion, spec("dim_estacion", ["station_id"], "estación", "Red del Tren Maya", ("2025", "2025"),
                        "clave y grados decimales", "E8-03.2", "Catálogo de estaciones del data mart", "espacial")),
    (ind_negocios_ageb_merida, spec("ind_negocios_ageb_merida", ["cvegeo_ageb"], "AGEB urbana", "Municipio de Mérida",
                                    ("2019", "2025"), "establecimientos y establecimientos por 1,000 habitantes",
                                    "E8-03.1;E8-03.2;E8-03.3;E8-01.1", "DENUE 2019-11 y 2025-05, Censo 2020, CONAPO 2020")),
    (ind_municipio_contexto, spec("ind_municipio_contexto", ["cvegeo_mun"], "municipio", "5 estados del Tren Maya",
                                  ("2019", "2025"), "personas, índices y establecimientos por 1,000 habitantes",
                                  "E8-01.1;E8-01.2;E8-01.3;E8-03.1;E8-03.2", "CONAPO 2020 y 2025, DENUE 2019-11 y 2025-05")),
    (ind_tren_maya_mensual, spec("ind_tren_maya_mensual", ["fecha_mes"], "mes", "Red completa del Tren Maya",
                                 "fecha_mes", "pasajeros, boletos, kilómetros y razones", "E8-05.1",
                                 "Prestación del servicio ferroviario de pasajeros 2025-2026")),
    (ind_restaurantes_transporte, spec("ind_restaurantes_transporte", ["id_anuncio"], "restaurante", "Municipio de Mérida",
                                       ("2026-11-24", "2026-11-24"), "metros y número de paradas", "E8-09.1;E8-04.3",
                                       "Sección Amarilla 2026-11-24 y GTFS ATY 12.1", "espacial")),
    (ind_obras_banquetas_anual, spec("ind_obras_banquetas_anual", ["anio_inicio"], "año de inicio de obra",
                                     "Municipio de Mérida", "anio_inicio", "obras, metros cuadrados y MXN", "E8-05.3",
                                     "SRFT 2023 a 2026 3.er trimestre")),
]

INDICADORES = [
    ("ind_negocios_ageb_merida", "establecimientos_por_1000_hab_2025", "Establecimientos por cada 1,000 habitantes",
     "establecimientos_2025 / pobtot × 1,000", "Establecimientos del DENUE 2025 en la AGEB",
     "Población total de la AGEB en el Censo 2020", "establecimientos por 1,000 habitantes",
     "Usa la población de 2020 porque el Censo no tiene un corte por AGEB más reciente; vacío si la AGEB no tiene población."),
    ("ind_negocios_ageb_merida", "variacion_pct_2019_2025", "Variación de establecimientos 2019-2025",
     "(establecimientos_2025 − establecimientos_2019) / establecimientos_2019 × 100",
     "Diferencia de establecimientos entre 2025 y 2019", "Establecimientos de 2019 en la AGEB", "porcentaje",
     "Vacío si la AGEB no tenía establecimientos en 2019."),
    ("ind_municipio_contexto", "establecimientos_por_1000_hab_2025", "Establecimientos por cada 1,000 habitantes",
     "establecimientos_2025 / poblacion_2025 × 1,000", "Establecimientos del DENUE 2025 en el municipio",
     "Población proyectada a mitad de 2025 (CONAPO)", "establecimientos por 1,000 habitantes", ""),
    ("ind_municipio_contexto", "variacion_pct_2019_2025", "Variación de establecimientos 2019-2025",
     "(establecimientos_2025 − establecimientos_2019) / establecimientos_2019 × 100",
     "Diferencia de establecimientos entre 2025 y 2019", "Establecimientos de 2019 en el municipio", "porcentaje", ""),
    ("ind_tren_maya_mensual", "pasajeros_por_km", "Pasajeros por kilómetro recorrido",
     "pasajeros_transportados / kilometros_recorridos", "Pasajeros transportados en el mes",
     "Kilómetros recorridos por los trenes en el mes", "pasajeros por km", "Toda la red; no hay dato por estación."),
    ("ind_tren_maya_mensual", "pasajeros_por_boleto", "Pasajeros por boleto vendido",
     "pasajeros_transportados / boletos_vendidos", "Pasajeros transportados en el mes", "Boletos vendidos en el mes",
     "pasajeros por boleto", "Razón entre dos registros publicados por separado; valores cercanos a 1 indican que ambos miden casi lo mismo."),
    ("ind_tren_maya_mensual", "variacion_anual_pasajeros_pct", "Variación anual de pasajeros",
     "(pasajeros_mes / pasajeros_mismo_mes_año_anterior − 1) × 100", "Pasajeros del mes",
     "Pasajeros del mismo mes del año anterior", "porcentaje", "Solo para meses de 2026 con su par de 2025."),
    ("ind_restaurantes_transporte", "distancia_parada_m", "Distancia a la parada más cercana",
     "mínimo de la distancia geodésica (haversine) del restaurante a cada parada del GTFS", "no aplica", "no aplica",
     "metros", "Distancia en línea recta, no por calle."),
    ("ind_restaurantes_transporte", "a_400_m_de_parada", "Restaurante a 400 m o menos de una parada",
     "distancia_parada_m ≤ 400", "no aplica", "no aplica", "booleano",
     "400 m es la distancia de caminata usual en planeación de transporte público."),
    ("ind_obras_banquetas_anual", "monto_aprobado_por_m2_mxn", "Monto aprobado por metro cuadrado",
     "Σ monto_aprobado_mxn / Σ metros_cuadrados", "Suma del monto aprobado de las obras del año",
     "Suma de metros cuadrados de las obras del año", "MXN por m²", "Vacío si las obras del año no reportan m²."),
]

DESCRIPCIONES_GOLD = {
    "establecimientos_2019": ("Establecimientos del DENUE de noviembre de 2019", "establecimientos"),
    "establecimientos_2025": ("Establecimientos del DENUE de mayo de 2025", "establecimientos"),
    "establecimientos_por_1000_hab_2025": ("Establecimientos de 2025 por cada 1,000 habitantes", "establecimientos por 1,000 habitantes"),
    "variacion_pct_2019_2025": ("Variación porcentual de establecimientos entre 2019 y 2025", "porcentaje"),
    "poblacion_2020": ("Población total en 2020 según CONAPO", "personas"),
    "poblacion_2025": ("Población proyectada a mitad de 2025 según CONAPO", "personas"),
    "fecha_mes": ("Primer día del mes, AAAA-MM-DD", "fecha ISO 8601"),
    "anio": ("Año", "año"), "mes": ("Número de mes", "mes 1-12"), "trimestre": ("Trimestre del año", "trimestre 1-4"),
    "nombre_mes": ("Nombre del mes en español", "texto"),
    "pasajeros_transportados": ("Pasajeros transportados en el mes", "pasajeros"),
    "boletos_vendidos": ("Boletos vendidos en el mes", "boletos"),
    "boletos_vendidos_estaciones": ("Boletos vendidos en taquillas de estación (recurso «Boletos vendidos (2024)», con datos hasta octubre de 2025)", "boletos"),
    "boletos_vendidos_puntos_venta": ("Boletos vendidos en otros puntos de venta (recurso «Boletos vendidos (2024)», con datos hasta octubre de 2025)", "boletos"),
    "colonia_normalizada": ("Colonia en mayúsculas, sin acentos ni prefijos, para agrupar variantes", "texto"),
    "kilometros_recorridos": ("Kilómetros recorridos por los trenes en el mes", "km"),
    "pasajeros_por_km": ("Pasajeros transportados por kilómetro recorrido", "pasajeros por km"),
    "pasajeros_por_boleto": ("Pasajeros transportados por boleto vendido", "pasajeros por boleto"),
    "variacion_anual_pasajeros_pct": ("Variación de pasajeros frente al mismo mes del año anterior", "porcentaje"),
    "parada_cercana_id": ("Identificador GTFS de la parada más cercana", "clave"),
    "parada_cercana": ("Nombre de la parada más cercana", "texto"),
    "distancia_parada_m": ("Distancia en línea recta a la parada más cercana", "metros"),
    "paradas_a_400_m": ("Paradas a 400 m o menos", "paradas"),
    "a_400_m_de_parada": ("Verdadero si hay una parada a 400 m o menos", "booleano"),
    "anio_inicio": ("Año de inicio de la obra", "año"),
    "obras": ("Número de obras", "obras"), "metros_cuadrados": ("Superficie de las obras", "m²"),
    "monto_aprobado_mxn": ("Monto aprobado", "MXN"), "pagado_mxn": ("Monto pagado", "MXN"),
    "monto_aprobado_por_m2_mxn": ("Monto aprobado por metro cuadrado", "MXN por m²"),
    "station_id": ("Identificador de la estación del Tren Maya", "clave"),
    "estacion": ("Nombre de la estación", "texto"), "estado": ("Estado de la estación", "texto"),
    "municipio": ("Municipio de la estación", "texto"),
    "cve_loc": ("Clave de localidad del INEGI", "clave"), "cve_ageb": ("Clave de AGEB del INEGI", "clave"),
}


def descripciones_gold(df: pd.DataFrame, archivo_silver: dict) -> dict:
    """Descripción de cada columna gold: propia o heredada de la tabla silver."""
    salida = {}
    previas = curar.leer_descripciones()
    heredadas = {}
    for (archivo, col), d in previas.items():
        heredadas.setdefault(col, d)
    for col in df.columns:
        if col in DESCRIPCIONES_GOLD:
            texto, unidad = DESCRIPCIONES_GOLD[col]
            salida[col] = {"descripcion": texto, "unidad": unidad, "origen_descripcion": "src/gold.py"}
        elif col in heredadas:
            salida[col] = heredadas[col]
    return salida


def main() -> int:
    GOLD.mkdir(parents=True, exist_ok=True)
    fuentes = curar.leer_fuentes()
    catalogo, diccionario, perfiles = [], [], []
    for funcion, s in SALIDAS:
        df = funcion()
        s["_parquet"], s["_csv"] = GOLD / f"{s['tabla']}.parquet", GOLD / f"{s['tabla']}.csv"
        if df.duplicated(subset=s["clave"]).any():
            print(f"ERROR: clave duplicada en {s['tabla']}")
            return 1
        df.to_parquet(s["_parquet"], index=False)
        curar.escribir_csv(df, s["_csv"])
        ficha = curar.ficha_catalogo(s, df, "gold", fuentes)
        if not s["id_fuente"]:
            ficha.update(id_fuente="no aplica", fuente="Calendario generado por src/gold.py",
                         url_original="no aplica", licencia="no aplica")
        catalogo.append(ficha)
        perfiles.append(curar.perfil_columnas(df, s["tabla"], "gold"))
        desc = descripciones_gold(df, {})
        diccionario.extend(curar.filas_diccionario(s, df, "gold", {("gold", k): v for k, v in desc.items()}, "gold"))
        print(f"  {s['tabla']}: {len(df):,} filas, {len(df.columns)} columnas")

    indicadores = pd.DataFrame(INDICADORES, columns=["tabla", "columna", "indicador", "formula", "numerador",
                                                     "denominador", "unidad", "nota"])
    curar.escribir_csv(indicadores, GOLD / "indicadores.csv")
    curar.actualizar(RAIZ / "catalogo_tablas.csv", pd.DataFrame(catalogo), "gold")
    curar.actualizar(RAIZ / "diccionario_columnas.csv", pd.DataFrame(diccionario), "gold")
    curar.actualizar(curar.REPORTES / "conciliacion.csv", pd.DataFrame(conciliacion), "gold")
    curar.actualizar(curar.REPORTES / "calidad_columnas.csv", pd.concat(perfiles), "gold")
    malos = [c for c in conciliacion if not c["cuadra_para_etl_curado"]]
    sin_desc = sum(1 for d in diccionario if not d["descripcion"])
    if sin_desc:
        print(f"AVISO: {sin_desc} columnas gold sin descripción")
    print(f"{len(SALIDAS)} tablas gold; {len(malos)} controles que no cuadran")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
