# Reporte de calidad

Generado: 2026-11-27. Se regenera con `python src/curar.py`, `python src/gold.py` y `python src/reporte_calidad.py`.

## Resumen

- **Silver:** 24 tablas curadas. 55,052 registros de entrada: 55,047 curados y 5 rechazados, que se conservan en `datos/rechazados/`.
- **Conteos de silver:** cuadran en 24 de 24 tablas (entrada = curados + rechazados). En 12 tablas además coincide el conteo independiente del archivo original.
- **Gold:** 10 tablas (dimensiones e indicadores). Sus 13 controles de totales cuadran en 13.
- **Diccionario:** 668 columnas documentadas; 0 sin descripción.
- **Claves:** son únicas en todas las tablas. La regla R3 rechaza los duplicados y gold verifica la clave antes de escribir.

## Conciliación por tabla

| Capa | Tabla | Original | Para ETL | Curado | Rechazados | Original = para ETL | Para ETL = curado + rechazados | Nota |
|---|---|---|---|---|---|---|---|---|
| silver | aty_paraderos | 3256 | 3256 | 3256 | 0 | sí | sí |  |
| silver | aty_r901_horario_publicado | — | 20 | 20 | 0 | sin conteo independiente | sí | Sin conteo independiente del original. |
| silver | aty_r901_paradas | — | 10 | 10 | 0 | sin conteo independiente | sí | Sin conteo independiente del original. |
| silver | aty_r901_tarifas | — | 6 | 6 | 0 | sin conteo independiente | sí | Sin conteo independiente del original. |
| silver | aty_r901_viajes | — | 80 | 80 | 0 | sin conteo independiente | sí | Sin conteo independiente del original. |
| silver | conapo_accesibilidad_localidad_yucatan | 2434 | 2434 | 2434 | 0 | sí | sí |  |
| silver | conapo_accesibilidad_municipal | 270 | 270 | 270 | 0 | sí | sí |  |
| silver | conapo_indicadores_demograficos_municipal | 13821 | 13821 | 13821 | 0 | sí | sí |  |
| silver | conapo_marginacion_ageb_yucatan_2020 | 1220 | 1220 | 1220 | 0 | sí | sí |  |
| silver | conapo_marginacion_municipal_2020 | 270 | 270 | 270 | 0 | sí | sí |  |
| silver | conapo_poblacion_quinquenal_municipal | 27642 | 27642 | 27642 | 0 | sí | sí |  |
| silver | inegi_censo_2020_ageb_yucatan | 1532 | 1532 | 1532 | 0 | sí | sí | Del original se toman solo los renglones de total por AGEB (MZA = 000 y AGEB distinta de 0000). |
| silver | inegi_mg_ageb_urbana_yucatan | 1562 | 1562 | 1562 | 0 | sí | sí | Una fila por polígono de AGEB urbana; la geometría completa está en ageb_urbana_yucatan_poligonos.geojson. |
| silver | osm_infraestructura_ciclista | 1198 | 1198 | 1198 | 0 | sí | sí | Se cuentan los elementos de la respuesta de Overpass que traen coordenada o geometría. |
| silver | osm_unidades_deportivas | 825 | 825 | 825 | 0 | sí | sí | Se cuentan los elementos de la respuesta de Overpass que traen coordenada o centro. |
| silver | rutatrenmaya_conexiones_teya | — | 3 | 3 | 0 | sin conteo independiente | sí | Sin conteo independiente del original. |
| silver | rutatrenmaya_tarifas_teya | — | 202 | 202 | 0 | sin conteo independiente | sí | Sin conteo independiente del original. |
| silver | seccion_amarilla_restaurantes_merida | — | 400 | 395 | 5 | sin conteo independiente | sí | 20 páginas de 20 anuncios; el original es HTML. |
| silver | siegy_aviacion_2025_12 | — | 11 | 11 | 0 | sin conteo independiente | sí | El original es un PDF de una página; cada renglón cita su fragmento de texto. |
| silver | siegy_resiliencia_turismo_2025_02 | — | 24 | 24 | 0 | sin conteo independiente | sí | El original es un PDF de una página; cada renglón cita su fragmento de texto. |
| silver | siegy_turismo_2025_09 | — | 11 | 11 | 0 | sin conteo independiente | sí | El original es un PDF de una página; cada renglón cita su fragmento de texto. |
| silver | srft_obras_banquetas_merida | — | 101 | 101 | 0 | sin conteo independiente | sí | Filtro de proyectos de guarniciones y banquetas del municipio de Mérida sobre los extractos del SRFT. |
| silver | tren_maya_horarios | — | 32 | 32 | 0 | sin conteo independiente | sí | El original es una tabla HTML; no hay conteo independiente. |
| silver | tren_maya_servicio_mensual | 122 | 122 | 122 | 0 | sí | sí | Formato largo: un renglón por variable y periodo; los boletos de 2024 traen 2 variables por registro. |

Controles de la capa gold:

| Tabla | Entrada | Salida | Cuadra | Control |
|---|---|---|---|---|
| ind_ageb_entorno_merida | 3256 | 2551 | sí | paradas_transporte: 3256 = 2551 en AGEB urbanas de Mérida + 450 en AGEB de otros municipios + 255 fuera de AGEB urbana |
| ind_ageb_entorno_merida | 193 | 189 | sí | restaurantes_seccion_amarilla: 193 = 189 en AGEB urbanas de Mérida + 3 en AGEB de otros municipios + 1 fuera de AGEB urbana |
| ind_ageb_entorno_merida | 825 | 733 | sí | instalaciones_deportivas: 825 = 733 en AGEB urbanas de Mérida + 0 en AGEB de otros municipios + 92 fuera de AGEB urbana |
| ind_ageb_entorno_merida | 99 | 98 | sí | estacionamientos_bicicleta: 99 = 98 en AGEB urbanas de Mérida + 0 en AGEB de otros municipios + 1 fuera de AGEB urbana |
| ind_ageb_entorno_merida | 702 | 617 | sí | instalaciones_deportivas_publicas: 702 = 617 en AGEB urbanas de Mérida + 0 en AGEB de otros municipios + 85 fuera de AGEB urbana |
| ind_ageb_entorno_merida | 194802 | 194801 | sí | km de ciclovías y carriles asignados por el punto medio de cada tramo: 194.8 km en AGEB urbanas de Mérida |
| ind_municipio_contexto | 533275 | 270 | sí | DENUE 2019 5 estados: 533275 = 533275 en municipios de CONAPO 2020 + 0 en municipios creados después de 2020 |
| ind_municipio_contexto | 604594 | 270 | sí | DENUE 2025 5 estados: 604594 = 603325 en municipios de CONAPO 2020 + 1269 en municipios creados después de 2020 |
| ind_negocios_ageb_merida | 53183 | 526 | sí | DENUE 2019 Mérida: 53183 establecimientos = 52675 en AGEB urbanas del Censo + 505 en AGEB sin renglón urbano en el Censo + 3 sin AGEB |
| ind_negocios_ageb_merida | 56014 | 526 | sí | DENUE 2025 Mérida: 56014 establecimientos = 55864 en AGEB urbanas del Censo + 150 en AGEB sin renglón urbano en el Censo + 0 sin AGEB |
| ind_obras_banquetas_anual | 101 | 5 | sí | 101 obras en silver = 101 sumadas por año; monto 87,181,317.01 = 87,181,317.01 |
| ind_restaurantes_transporte | 193 | 193 | sí | 193 restaurantes con coordenadas; 184 a 400 m o menos de una parada |
| ind_tren_maya_mensual | 83 | 21 | sí | Pasajeros 2025-2026: 2,225,282 en silver = 2,225,282 en gold |

## Registros rechazados

| Tabla | Regla | Motivo | Filas |
|---|---|---|---|
| seccion_amarilla_restaurantes_merida | P1 | el anuncio declara un municipio distinto de Mérida | 5 |

Las reglas están descritas en `src/curar.py`.

## Columnas con más vacíos

Columnas con 20 % o más de valores vacíos. El dato falta en la fuente; no se imputa.

| Capa | Tabla | Columna | Vacíos (%) |
|---|---|---|---|
| silver | aty_r901_tarifas | texto_publicado | 33.3 |
| silver | inegi_censo_2020_ageb_yucatan | p6a11_noaf | 34.6 |
| silver | inegi_censo_2020_ageb_yucatan | p6a11_noam | 33.3 |
| silver | inegi_censo_2020_ageb_yucatan | p8a14an_f | 33.3 |
| silver | inegi_censo_2020_ageb_yucatan | p12a14noaf | 33.0 |
| silver | inegi_censo_2020_ageb_yucatan | p8a14an_m | 32.5 |
| silver | inegi_censo_2020_ageb_yucatan | p12a14noam | 32.4 |
| silver | inegi_censo_2020_ageb_yucatan | vph_pisoti | 32.2 |
| silver | inegi_censo_2020_ageb_yucatan | vph_s_elec | 29.1 |
| silver | inegi_censo_2020_ageb_yucatan | p12a14noa | 27.5 |
| silver | inegi_censo_2020_ageb_yucatan | pdesocup_f | 26.8 |
| silver | inegi_censo_2020_ageb_yucatan | p8a14an | 26.0 |
| silver | inegi_censo_2020_ageb_yucatan | p6a11_noa | 26.0 |
| silver | inegi_censo_2020_ageb_yucatan | vph_snbien | 25.1 |
| silver | inegi_censo_2020_ageb_yucatan | vph_aguafv | 24.8 |
| silver | inegi_censo_2020_ageb_yucatan | p5_hli_nhe | 24.0 |
| silver | inegi_censo_2020_ageb_yucatan | p3hlinhe | 23.9 |
| silver | inegi_censo_2020_ageb_yucatan | p3hlinhe_f | 23.6 |
| silver | inegi_censo_2020_ageb_yucatan | vph_letr | 23.6 |
| silver | inegi_censo_2020_ageb_yucatan | vph_sintic | 23.6 |
| silver | inegi_censo_2020_ageb_yucatan | potras_rel | 23.4 |
| silver | inegi_censo_2020_ageb_yucatan | p3hlinhe_m | 22.6 |
| silver | inegi_censo_2020_ageb_yucatan | vph_ndeaed | 22.1 |
| silver | inegi_censo_2020_ageb_yucatan | pder_imssb | 21.3 |
| silver | osm_infraestructura_ciclista | segregada | 99.3 |
| silver | osm_infraestructura_ciclista | iluminado | 98.8 |
| silver | osm_infraestructura_ciclista | capacidad | 93.0 |
| silver | osm_infraestructura_ciclista | tipo_carril | 52.8 |
| silver | osm_infraestructura_ciclista | superficie | 50.8 |
| silver | osm_infraestructura_ciclista | nombre | 49.9 |
| silver | osm_unidades_deportivas | operador | 98.9 |
| silver | osm_unidades_deportivas | iluminado | 91.8 |
| silver | osm_unidades_deportivas | superficie | 90.2 |
| silver | osm_unidades_deportivas | nombre | 89.9 |
| silver | rutatrenmaya_conexiones_teya | duracion_min | 33.3 |
| silver | rutatrenmaya_conexiones_teya | ruta | 33.3 |
| silver | rutatrenmaya_tarifas_teya | horario | 98.0 |
| silver | rutatrenmaya_tarifas_teya | precio_mxn | 23.8 |
| silver | rutatrenmaya_tarifas_teya | duracion_texto | 23.8 |
| silver | rutatrenmaya_tarifas_teya | duracion_min | 23.8 |
| silver | seccion_amarilla_restaurantes_merida | lat | 51.1 |
| silver | seccion_amarilla_restaurantes_merida | lon | 51.1 |
| silver | seccion_amarilla_restaurantes_merida | url_ficha | 47.6 |
| silver | srft_obras_banquetas_merida | metros_lineales | 100.0 |
| silver | tren_maya_horarios | tiempo_recorrido | 43.8 |
| gold | ind_tren_maya_mensual | variacion_anual_pasajeros_pct | 57.1 |
| gold | ind_tren_maya_mensual | boletos_vendidos_estaciones | 52.4 |
| gold | ind_tren_maya_mensual | boletos_vendidos_puntos_venta | 52.4 |

## Cobertura

| Capa | Tabla | Granularidad | Cobertura | Territorio | Filas |
|---|---|---|---|---|---|
| gold | dim_ageb | AGEB urbana | 2020 a 2020 | Yucatán | 1532 |
| gold | dim_estacion | estación | 2025 a 2025 | Red del Tren Maya | 34 |
| gold | dim_municipio | municipio | 2020 a 2020 | 5 estados del Tren Maya | 270 |
| gold | dim_tiempo | mes | 2019-01-01 a 2026-12-01 | no aplica | 96 |
| gold | ind_ageb_entorno_merida | AGEB urbana | 2020 a 2026 | Municipio de Mérida | 545 |
| gold | ind_municipio_contexto | municipio | 2019 a 2025 | 5 estados del Tren Maya | 270 |
| gold | ind_negocios_ageb_merida | AGEB urbana | 2019 a 2025 | Municipio de Mérida | 526 |
| gold | ind_obras_banquetas_anual | año de inicio de obra | 2022 a 2026 | Municipio de Mérida | 5 |
| gold | ind_restaurantes_transporte | restaurante | 2026-11-24 a 2026-11-24 | Municipio de Mérida | 193 |
| gold | ind_tren_maya_mensual | mes | 2025-01-01 a 2026-09-01 | Red completa del Tren Maya | 21 |
| silver | aty_paraderos | parada | 2026-11-24 a 2026-11-24 | Zona metropolitana de Mérida | 3256 |
| silver | aty_r901_horario_publicado | corrida por sentido | 2026-11-24 a 2026-11-24 | Ruta R901 La Plancha – Teya | 20 |
| silver | aty_r901_paradas | parada por sentido | 2026-11-24 a 2026-11-24 | Ruta R901 La Plancha – Teya | 10 |
| silver | aty_r901_tarifas | tarifa por tipo de usuario | 2026-11-24 a 2026-11-24 | Ruta R901 | 6 |
| silver | aty_r901_viajes | viaje programado | 2026-01-01 a 2026-11-27 | Ruta R901 La Plancha – Teya | 80 |
| silver | conapo_accesibilidad_localidad_yucatan | localidad | 2020 a 2020 | Yucatán | 2434 |
| silver | conapo_accesibilidad_municipal | municipio | 2020 a 2020 | 5 estados del Tren Maya | 270 |
| silver | conapo_indicadores_demograficos_municipal | municipio por año | 1990 a 2040 | 5 estados del Tren Maya | 13821 |
| silver | conapo_marginacion_ageb_yucatan_2020 | AGEB urbana | 2020 a 2020 | Yucatán | 1220 |
| silver | conapo_marginacion_municipal_2020 | municipio | 2020 a 2020 | 5 estados del Tren Maya | 270 |
| silver | conapo_poblacion_quinquenal_municipal | municipio por sexo y año | 1990 a 2040 | 5 estados del Tren Maya | 27642 |
| silver | inegi_censo_2020_ageb_yucatan | AGEB urbana | 2020 a 2020 | Yucatán | 1532 |
| silver | inegi_mg_ageb_urbana_yucatan | AGEB urbana | 2025-12 a 2025-12 | Yucatán | 1562 |
| silver | osm_infraestructura_ciclista | tramo de ciclovía o carril, o estacionamiento de bicicletas | 2026-11-25 a 2026-11-25 | Municipio de Mérida | 1198 |
| silver | osm_unidades_deportivas | instalación deportiva | 2026-11-25 a 2026-11-25 | Municipio de Mérida | 825 |
| silver | rutatrenmaya_conexiones_teya | conexión de transporte | 2026-11-24 a 2026-11-24 | Estación Teya-Mérida | 3 |
| silver | rutatrenmaya_tarifas_teya | tarifa por destino y tipo | 2026-11-24 a 2026-11-24 | Desde la estación Teya-Mérida | 202 |
| silver | seccion_amarilla_restaurantes_merida | anuncio de negocio | 2026-11-24 a 2026-11-24 | Municipio de Mérida | 395 |
| silver | siegy_aviacion_2025_12 | indicador por periodo y territorio | 2024 a 2025 | México, Yucatán y aeropuerto de Mérida | 11 |
| silver | siegy_resiliencia_turismo_2025_02 | indicador por periodo y territorio | 2019 a 2024 | Yucatán y zonas arqueológicas | 24 |
| silver | siegy_turismo_2025_09 | indicador por periodo y territorio | 2024 a 2025 | Yucatán | 11 |
| silver | srft_obras_banquetas_merida | obra (proyecto SRFT) | 2022-04-18 a 2026-09-28 | Municipio de Mérida | 101 |
| silver | tren_maya_horarios | tramo de circulación | 2026-11-24 a 2026-11-24 | Red del Tren Maya | 32 |
| silver | tren_maya_servicio_mensual | variable por mes (2024: por periodo publicado) | 2023-12-12 a 2026-09-01 | Red completa del Tren Maya | 122 |
