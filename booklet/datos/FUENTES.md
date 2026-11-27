# Fuentes y método · Del tren a la calle

Todos los archivos de esta carpeta salen de datos públicos reales del repositorio y se regeneran con `python src/booklet.py`. Solo usan fuentes públicas y no traen datos personales.

## `escena-1.csv` y `escena-2.csv`

- **Contenido:**
  - `escena-1.csv`: negocios en tres anillos de distancia (0-1, 1-3 y 3-5 km) alrededor de las 34 estaciones del Tren Maya, en 2019 y 2025, con el cambio absoluto y porcentual.
  - `escena-2.csv`: lo mismo por estación, a 5 km. Trae su lugar en el ranking, estado, municipio, coordenadas (`lat`, `lon`), orden en la ruta (`orden_ruta`, según el número del catálogo) y cuántas estaciones tiene su estado.
  - `estados_tren_maya.geojson`: contorno de los 5 estados del Tren Maya, base del mapa de la escena 2.
- **Fuentes:**
  - INEGI, DENUE noviembre 2019 y mayo 2025, de Campeche, Chiapas, Quintana Roo, Tabasco y Yucatán, descarga masiva por estado (por ejemplo, Yucatán: <https://www.inegi.org.mx/contenidos/masiva/denue/2019_11/denue_31_1119_csv.zip> y <https://www.inegi.org.mx/contenidos/masiva/denue/2025_05/denue_31_0525_csv.zip>; las URL de los cinco estados están en el `procedencia.json` de `datos/originales/03_inegi/3.1_denue_2019_11/` y `3.2_denue_2025_05/`)
  - Catálogo de estaciones del Tren Maya: `procesamiento/03_denue_datamart/data/reference/estaciones_tren_maya_catalogo_maestro.csv`, con coordenadas del mapa oficial (<https://trenmaya.gob.mx/>) y cotejo secundario.
- **Corte:** DENUE de noviembre de 2019 y de mayo de 2025, descargados el 24 de noviembre de 2026.
- **Licencia:** Términos de libre uso de la información del INEGI.
- **Cálculo:**
  - El data mart del equipo (`procesamiento/03_denue_datamart/`) asigna cada negocio a su estación más cercana y lo clasifica por anillo de distancia. Así ningún negocio se cuenta dos veces.
  - Los datos se toman de `data/processed/station_ring_change_2019_2025.csv`.
  - Las estaciones sin negocios a 5 km (Edzná y Calakmul) quedan en cero.
  - El script comprueba que los totales de las dos escenas coincidan entre sí y con el data mart: 39,350 negocios en 2019 y 44,838 en 2025.

- **Contorno de los estados:**
  - Fuente: INEGI, Marco Geoestadístico de diciembre de 2025, servicio `wscatgeo` (<https://gaia.inegi.org.mx/wscatgeo/v2/geo/mgee/04>; igual para 07, 23, 27 y 31).
  - Originales: `datos/originales/03_inegi/3.3_censo_2020_ageb/mg_estado_NN.geojson`.
  - Se conservan los polígonos de más de unos 25 km² y se simplifican con Ramer-Douglas-Peucker a cerca de 1 km (0.01°).

## `escena-3.csv`

- **Contenido:** pasajeros transportados y boletos vendidos por mes en toda la red, de enero de 2025 a septiembre de 2026, y la variación contra el mismo mes del año anterior.
- **Fuente:** Tren Maya, prestación del servicio ferroviario de pasajeros, en datos.gob.mx: <https://www.datos.gob.mx/dataset/prestacion_servicio_ferroviario_pasajeros>. Tabla gold `datos/gold/ind_tren_maya_mensual.csv`.
- **Corte:** septiembre de 2026; descargado el 24 de noviembre de 2026.
- **Licencia:** CC BY 4.0.
- **Cálculo:** `variacion_anual_pct = (pasajeros del mes / pasajeros del mismo mes de 2025 − 1) × 100`. Solo existe para los meses de 2026.

## `escena-4.csv` y `merida_ageb.geojson`

- **Contenido:**
  - `escena-4.csv`: las 526 AGEB urbanas del municipio de Mérida (31050) con datos. Trae la población de 2020, los negocios de 2019 y de 2025, el cambio, los negocios por cada 1,000 habitantes, el grado de marginación de 2020 y la distancia en línea recta del centro de la AGEB a la estación Teya.
  - `merida_ageb.geojson`: los 545 polígonos de AGEB urbanas de Mérida del Marco Geoestadístico 2025, en EPSG:4326 y simplificados para dibujar. La propiedad `con_dato` indica si la AGEB está en `escena-4.csv`.
- **Fuentes:**
  - INEGI, DENUE noviembre 2019 y mayo 2025.
  - INEGI, Censo de Población y Vivienda 2020 por AGEB urbana: <https://www.inegi.org.mx/programas/ccpv/2020/>
  - INEGI, Marco Geoestadístico, diciembre de 2025, servicio `wscatgeo`: <https://gaia.inegi.org.mx/wscatgeo/v2/geo/agebu/31>
  - CONAPO, índice de marginación urbana 2020 por AGEB: <https://www.datos.gob.mx/dataset/indices_marginacion>
- **Tabla gold:** `datos/gold/ind_negocios_ageb_merida.csv`.
- **Licencia:**
  - INEGI: términos de libre uso.
  - CONAPO: CC BY 4.0.
- **Cálculo:**
  - `cambio = negocios_2025 − negocios_2019`.
  - `cambio_pct` queda vacío si la AGEB no tenía negocios en 2019.
  - La distancia a Teya se mide con la fórmula de haversine, desde el promedio de los vértices de la AGEB.
  - Los polígonos se simplifican con Ramer-Douglas-Peucker a unos 9 m (0.00008°) y sus coordenadas se redondean a 5 decimales.
  - Los anillos van en el sentido que usa D3: el exterior, en sentido horario.
  - Las 19 AGEB nuevas del Marco 2025 no están en el Censo 2020: tienen polígono, pero no dato.
