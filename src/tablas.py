"""Especificación de las tablas curadas del equipo E8.

Una entrada por tabla de datos/para-etl. Cada entrada declara lo que el
catálogo exige: clave, granularidad, cobertura temporal, territorio, unidad,
versión de la fuente y formato. También declara cómo contar los registros del
original para conciliar cantidades entre capas y qué reglas de calidad propias
aplican además de las generales de src/curar.py.

Formato (clasificación por tipo de dato, no por institución):
- tabular: tablas de registros (CSV, JSON, XLSX).
- espacial: registros con geometría o coordenadas como dato principal.
- documento: cifras transcritas de PDF.
- web: tablas extraídas de páginas HTML.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ORIG = RAIZ / "datos" / "originales"
ETL = "datos/para-etl"
RESPONSABLE = "Equipo E8, Del tren a la calle (UPY 9B)"


# --- Conteos de los originales -------------------------------------------

def registros_ckan(*rutas: str) -> int:
    return sum(len(json.loads((ORIG / r).read_text(encoding="utf-8"))["records"]) for r in rutas)


def conteo_censo_ageb() -> int:
    ruta = ORIG / "03_inegi/3.3_censo_2020_ageb/ageb_mza_urbana_31_cpv2020_csv.zip"
    with zipfile.ZipFile(ruta) as z:
        nombre = next(n for n in z.namelist() if n.endswith(".csv") and "conjunto_de_datos" in n)
        df = pd.read_csv(io.TextIOWrapper(z.open(nombre), encoding="utf-8-sig"), dtype=str,
                         usecols=["MZA", "AGEB"])
    return int(((df["MZA"] == "000") & (df["AGEB"] != "0000")).sum())


def conteo_gtfs(tabla: str) -> int:
    with zipfile.ZipFile(ORIG / "04_geoportal_merida/4.3_paraderos/gtfs_va_y_ven_aty.zip") as z:
        return len(pd.read_csv(z.open(tabla), dtype=str))


def conteo_tren_maya() -> int:
    """La tabla mensual pasa a formato largo: un renglón por variable y periodo."""
    base = "05_solicitud_datos/5.1_tren_maya_pasajeros/"
    sencillos = registros_ckan(*(base + f"{v}_{a}.json" for v in ("pasajeros", "boletos", "kilometros")
                                 for a in (2025, 2026) if (ORIG / base / f"{v}_{a}.json").exists()))
    pasajeros_2024 = registros_ckan(base + "pasajeros_2024.json")
    boletos_2024 = registros_ckan(base + "boletos_2024.json") * 2  # estaciones y puntos de venta
    return sencillos + pasajeros_2024 + boletos_2024


# --- Tablas ----------------------------------------------------------------

def t(**kw) -> dict:
    kw.setdefault("reglas", [])
    kw.setdefault("conteo_original", None)
    kw.setdefault("nota_conciliacion", "")
    kw.setdefault("responsable", RESPONSABLE)
    kw["archivo"] = f"{ETL}/{kw['archivo']}"
    return kw


CONAPO = "datos.gob.mx, metadata_modified 2026-11-13"
DENUE = "INEGI"

TABLAS = [
    t(tabla="conapo_marginacion_municipal_2020", id_fuente="E8-01.1", formato="tabular",
      archivo="01_datos_gob/1.1_conapo_marginacion/marginacion_municipal_2020.csv",
      clave=["cvegeo_mun"], granularidad="municipio", territorio="5 estados del Tren Maya",
      cobertura=("2020", "2020"), unidad="porcentaje de población por carencia; índice adimensional",
      version_fuente=f"Índice de marginación municipal 2020 ({CONAPO})",
      conteo_original=lambda: registros_ckan("01_datos_gob/1.1_conapo_marginacion/imm_2020_municipal_5_estados.json")),
    t(tabla="conapo_marginacion_ageb_yucatan_2020", id_fuente="E8-01.1", formato="tabular",
      archivo="01_datos_gob/1.1_conapo_marginacion/marginacion_urbana_ageb_yucatan_2020.csv",
      clave=["cvegeo_ageb"], granularidad="AGEB urbana", territorio="Yucatán",
      cobertura=("2020", "2020"), unidad="porcentaje de población por carencia; índice adimensional",
      version_fuente=f"Índice de marginación urbana por AGEB 2020 ({CONAPO})",
      conteo_original=lambda: registros_ckan("01_datos_gob/1.1_conapo_marginacion/imu_2020_ageb_yucatan.json")),
    t(tabla="conapo_indicadores_demograficos_municipal", id_fuente="E8-01.2", formato="tabular",
      archivo="01_datos_gob/1.2_conapo_proyecciones/indicadores_demograficos_municipal.csv",
      clave=["cvegeo_mun", "ano"], granularidad="municipio por año", territorio="5 estados del Tren Maya",
      cobertura="ano", unidad="personas a mitad de año",
      version_fuente=f"Proyecciones de población, indicadores demográficos ({CONAPO})",
      conteo_original=lambda: registros_ckan("01_datos_gob/1.2_conapo_proyecciones/pobproy_inddemo_municipal_5_estados.json")),
    t(tabla="conapo_poblacion_quinquenal_municipal", id_fuente="E8-01.2", formato="tabular",
      archivo="01_datos_gob/1.2_conapo_proyecciones/poblacion_quinquenal_municipal.csv",
      clave=["cvegeo_mun", "sexo", "ano"], granularidad="municipio por sexo y año", territorio="5 estados del Tren Maya",
      cobertura="ano", unidad="personas a mitad de año",
      version_fuente=f"Población a mitad de año por municipio y grupo quinquenal ({CONAPO})",
      conteo_original=lambda: registros_ckan("01_datos_gob/1.2_conapo_proyecciones/pobproy_quinq_municipal_5_estados.json")),
    t(tabla="conapo_accesibilidad_municipal", id_fuente="E8-01.3", formato="tabular",
      archivo="01_datos_gob/1.3_conapo_accesibilidad/accesibilidad_municipal.csv",
      clave=["cvegeo_mun"], granularidad="municipio", territorio="5 estados del Tren Maya",
      cobertura=("2020", "2020"), unidad="personas y viviendas; grado de accesibilidad",
      version_fuente=f"Accesibilidad a centros urbanos, nivel municipal ({CONAPO})",
      conteo_original=lambda: registros_ckan("01_datos_gob/1.3_conapo_accesibilidad/acu_municipal_5_estados.json")),
    t(tabla="conapo_accesibilidad_localidad_yucatan", id_fuente="E8-01.3", formato="espacial",
      archivo="01_datos_gob/1.3_conapo_accesibilidad/accesibilidad_localidad_yucatan.csv",
      clave=["cvegeo_loc"], granularidad="localidad", territorio="Yucatán",
      cobertura=("2020", "2020"), unidad="personas y viviendas; grado de accesibilidad",
      version_fuente=f"Accesibilidad a centros urbanos, nivel localidad ({CONAPO})",
      conteo_original=lambda: registros_ckan("01_datos_gob/1.3_conapo_accesibilidad/acu_localidad_yucatan.json")),
    t(tabla="siegy_aviacion_2025_12", id_fuente="E8-02.1", formato="documento",
      archivo="02_siegy/2.1_boletin_aviacion_2025_12/indicadores.csv",
      clave=["indicador", "periodo", "territorio"], granularidad="indicador por periodo y territorio",
      territorio="México, Yucatán y aeropuerto de Mérida", cobertura=("2024", "2025"),
      unidad="según columna unidad (pasajeros, toneladas, porcentaje)",
      version_fuente="Boletín SIEGY Día de la Aviación Civil, diciembre de 2025",
      nota_conciliacion="El original es un PDF de una página; cada renglón cita su fragmento de texto."),
    t(tabla="siegy_turismo_2025_09", id_fuente="E8-02.2", formato="documento",
      archivo="02_siegy/2.2_boletin_turismo_2025_09/indicadores.csv",
      clave=["indicador", "periodo", "territorio"], granularidad="indicador por periodo y territorio",
      territorio="Yucatán", cobertura=("2024", "2025"),
      unidad="según columna unidad (turistas, pasajeros, visitantes, porcentaje)",
      version_fuente="Boletín SIEGY Día Mundial del Turismo, septiembre de 2025",
      nota_conciliacion="El original es un PDF de una página; cada renglón cita su fragmento de texto."),
    t(tabla="siegy_resiliencia_turismo_2025_02", id_fuente="E8-02.3", formato="documento",
      archivo="02_siegy/2.3_boletin_resiliencia_turismo_2025_02/indicadores.csv",
      clave=["indicador", "periodo", "territorio"], granularidad="indicador por periodo y territorio",
      territorio="Yucatán y zonas arqueológicas", cobertura=("2019", "2024"),
      unidad="según columna unidad (turistas, visitantes, porcentaje)",
      version_fuente="Boletín SIEGY Día Mundial de la Resiliencia del Turismo, febrero de 2025",
      nota_conciliacion="El original es un PDF de una página; cada renglón cita su fragmento de texto."),
    t(tabla="inegi_censo_2020_ageb_yucatan", id_fuente="E8-03.3", formato="tabular",
      archivo="03_inegi/3.3_censo_2020_ageb/censo_2020_ageb_urbana_yucatan.csv",
      clave=["cvegeo_ageb"], granularidad="AGEB urbana", territorio="Yucatán",
      cobertura=("2020", "2020"), unidad="personas, viviendas y promedios",
      version_fuente="Censo de Población y Vivienda 2020, resultados por AGEB y manzana urbana (INEGI)",
      conteo_original=conteo_censo_ageb,
      nota_conciliacion="Del original se toman solo los renglones de total por AGEB (MZA = 000 y AGEB distinta de 0000)."),
    t(tabla="aty_paraderos", id_fuente="E8-04.3", formato="espacial",
      archivo="04_geoportal_merida/4.3_paraderos/paraderos_aty.csv",
      clave=["stop_id"], granularidad="parada", territorio="Zona metropolitana de Mérida",
      cobertura=("2026-11-24", "2026-11-24"), unidad="parada; número de rutas",
      version_fuente="GTFS del Sistema Va y Ven (ATY), versión 12.1",
      conteo_original=lambda: conteo_gtfs("stops.txt")),
    t(tabla="tren_maya_servicio_mensual", id_fuente="E8-05.1", formato="tabular",
      archivo="05_solicitud_datos/5.1_tren_maya_pasajeros/servicio_tren_maya_mensual.csv",
      clave=["variable", "periodo_inicio"], granularidad="variable por mes (2024: por periodo publicado)",
      territorio="Red completa del Tren Maya", cobertura="periodo_inicio",
      unidad="pasajeros, boletos o kilómetros según variable",
      version_fuente="Prestación del servicio ferroviario de pasajeros (datos.gob.mx, metadata_modified 2026-10-22)",
      conteo_original=conteo_tren_maya,
      nota_conciliacion="Formato largo: un renglón por variable y periodo; los boletos de 2024 traen 2 variables por registro."),
    t(tabla="aty_r901_horario_publicado", id_fuente="E8-05.2", formato="documento",
      archivo="05_solicitud_datos/5.2_aty_ruta_r901/r901_horario_publicado.csv",
      clave=["sentido", "corrida"], granularidad="corrida por sentido", territorio="Ruta R901 La Plancha – Teya",
      cobertura=("2026-11-24", "2026-11-24"), unidad="hora local",
      version_fuente="Horario publicado en transporteyucatan.org.mx/ietram"),
    t(tabla="aty_r901_paradas", id_fuente="E8-05.2", formato="espacial",
      archivo="05_solicitud_datos/5.2_aty_ruta_r901/r901_paradas.csv",
      clave=["direction_id", "orden"], granularidad="parada por sentido", territorio="Ruta R901 La Plancha – Teya",
      cobertura=("2026-11-24", "2026-11-24"), unidad="minutos y metros desde la salida",
      version_fuente="GTFS del Sistema Va y Ven (ATY), versión 12.1"),
    t(tabla="aty_r901_tarifas", id_fuente="E8-05.2", formato="web",
      archivo="05_solicitud_datos/5.2_aty_ruta_r901/r901_tarifas.csv",
      clave=["tipo_usuario", "fuente"], granularidad="tarifa por tipo de usuario", territorio="Ruta R901",
      cobertura=("2026-11-24", "2026-11-24"), unidad="MXN",
      version_fuente="transporteyucatan.org.mx/ietram y GTFS versión 12.1"),
    t(tabla="aty_r901_viajes", id_fuente="E8-05.2", formato="tabular",
      archivo="05_solicitud_datos/5.2_aty_ruta_r901/r901_viajes_gtfs.csv",
      clave=["trip_id"], granularidad="viaje programado", territorio="Ruta R901 La Plancha – Teya",
      cobertura="vigencia_inicio", unidad="hora local y minutos",
      version_fuente="GTFS del Sistema Va y Ven (ATY), versión 12.1"),
    t(tabla="srft_obras_banquetas_merida", id_fuente="E8-05.3", formato="espacial",
      archivo="05_solicitud_datos/5.3_ayuntamiento_banquetas/obras_banquetas_merida.csv",
      clave=["folio"], granularidad="obra (proyecto SRFT)", territorio="Municipio de Mérida",
      cobertura="fecha_inicio", unidad="MXN, metros cuadrados y metros lineales",
      version_fuente="SRFT, Transparencia Presupuestaria (SHCP), cortes 2023 a 2026 3.er trimestre",
      nota_conciliacion="Filtro de proyectos de guarniciones y banquetas del municipio de Mérida sobre los extractos del SRFT."),
    t(tabla="seccion_amarilla_restaurantes_merida", id_fuente="E8-09.1", formato="web",
      archivo="09_scraping/9.1_seccion_amarilla_restaurantes/restaurantes_merida.csv",
      clave=["id_anuncio"], granularidad="anuncio de negocio", territorio="Municipio de Mérida",
      cobertura="fecha_consulta", unidad="negocio",
      version_fuente="Sección Amarilla, 20 páginas de resultados consultadas el 2026-11-24",
      reglas=["coordenada_opcional", "fuera_de_merida", "colonia_normalizada"],
      nota_conciliacion="20 páginas de 20 anuncios; el original es HTML."),
    t(tabla="tren_maya_horarios", id_fuente="E8-09.2", formato="web",
      archivo="09_scraping/9.2_tren_maya_horarios/horarios_tren_maya.csv",
      clave=["circulacion", "tramo"], granularidad="tramo de circulación", territorio="Red del Tren Maya",
      cobertura="fecha_consulta", unidad="hora local y tiempo de recorrido",
      version_fuente="trenmaya.gob.mx/horarios.php consultada el 2026-11-24",
      nota_conciliacion="El original es una tabla HTML; no hay conteo independiente."),
    t(tabla="rutatrenmaya_conexiones_teya", id_fuente="E8-09.3", formato="web",
      archivo="09_scraping/9.3_guia_estacion_teya/conexiones_transporte.csv",
      clave=["servicio", "origen", "destino"], granularidad="conexión de transporte", territorio="Estación Teya-Mérida",
      cobertura="fecha_consulta", unidad="MXN y minutos",
      version_fuente="rutatrenmaya.mx, guía de la estación Teya-Mérida, consultada el 2026-11-24"),
    t(tabla="rutatrenmaya_tarifas_teya", id_fuente="E8-09.3", formato="web",
      archivo="09_scraping/9.3_guia_estacion_teya/tarifas_desde_teya.csv",
      clave=["tabla", "estacion_origen", "estacion_destino", "tipo_tarifa"],
      granularidad="tarifa por destino y tipo", territorio="Desde la estación Teya-Mérida",
      cobertura="fecha_consulta", unidad="MXN y minutos",
      version_fuente="rutatrenmaya.mx, guía de la estación Teya-Mérida, consultada el 2026-11-24"),
]
