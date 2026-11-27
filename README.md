# Del tren a la calle

**¿Qué tan al alcance están las oportunidades alrededor del Tren Maya?**

Equipo: Raúl Cetina, Ricardo Horta, Damián Novelo. Grupo 9B, Ingeniería de Datos, UPY.

Este repositorio reúne las 27 fuentes del equipo: 9 subtemas, un tipo de fuente por subtema y 3 fuentes por tipo. Cada fuente pasa por tres capas:

- **bronze:** el archivo original tal como se descargó, con URL, fecha UTC, licencia y SHA-256;
- **silver:** las tablas curadas, con tipos, codificación, fechas y claves territoriales corregidos. Los registros que no cumplen las reglas se conservan aparte, con su motivo;
- **gold:** dimensiones compartidas e indicadores con fórmula, numerador y denominador documentados.

Cada paso concilia sus conteos con el anterior, y todo se reproduce con un solo comando.

[Fuentes](#fuentes) · [Entregables](#entregables) · [Capas](#capas) · [Estructura](#estructura) · [Cómo reproducir](#cómo-reproducir) · [Claves para el ETL](#claves-para-el-etl) · [Pendientes del equipo](#pendientes-del-equipo) · [Licencias](LICENCIAS.md)

## Fuentes

Estado al 2026-11-27: **18 reales** y **9 simuladas** (subtemas 6, 7 y 8).

**Aviso:** las fuentes 6.1 a 8.3 y las tablas de respuesta a las 3 solicitudes (`datos/propios/`) son datos de práctica generados por el equipo, calibrados con las fuentes públicas; no son mediciones ni respuestas oficiales.

Las tablas generadas por el equipo están en `datos/propios/`. El catálogo completo, con licencia y fecha de descarga, está en [`fuentes.csv`](fuentes.csv).

| Subtema | Tipo | Fuente | Estado | Datos para el ETL |
|---|---|---|---|---|
| 1. El territorio antes de la conexión | Datos.gob.mx | 1.1 CONAPO, Índices de marginación 2020 | real | 270 municipios de los 5 estados y 1,220 AGEB urbanas de Yucatán |
| | | 1.2 CONAPO, Proyecciones de población | real | 27,642 filas por municipio, sexo y año, más 13,821 de indicadores |
| | | 1.3 CONAPO, Accesibilidad a centros urbanos | real | 270 municipios y 2,434 localidades de Yucatán con lat y lon |
| 2. La llegada de viajeros | SIEGY | 2.1 Boletín Día de la Aviación Civil, dic 2025 | real | 11 indicadores |
| | | 2.2 Boletín Día Mundial del Turismo, sep 2025 | real | 11 indicadores |
| | | 2.3 Boletín Día Mundial de la Resiliencia del Turismo, feb 2025 | real | 24 indicadores |
| 3. Los negocios que encuentra esa demanda | INEGI | 3.1 DENUE noviembre 2019 | real | 533,275 establecimientos; data mart en `procesamiento/` |
| | | 3.2 DENUE mayo 2025 | real | 604,594 establecimientos; data mart en `procesamiento/` |
| | | 3.3 Censo 2020 por AGEB y manzana urbana | real | 1,532 AGEB urbanas de Yucatán, y los polígonos de las 1,562 AGEB urbanas del Marco Geoestadístico 2025 |
| 4. Una ciudad preparada para recibirlos | Geoportal de Mérida | 4.1 Unidades deportivas | real (sustituto) | 825 instalaciones deportivas de OpenStreetMap en el municipio de Mérida, mientras se exporta la capa del Geoportal ([pasos](datos/originales/04_geoportal_merida/4.1_unidades_deportivas/PENDIENTE.md)) |
| | | 4.2 Circuito Enlace | real (sustituto) | 1,198 elementos de infraestructura ciclista de OpenStreetMap en Mérida (241 km de ciclovías y carriles), porque el recorrido no se publica fuera del Geoportal ([detalle](datos/originales/04_geoportal_merida/4.2_circuito_enlace/PENDIENTE.md)) |
| | | 4.3 Paraderos de transporte público | real (sustituto) | 3,256 paradas del GTFS oficial del Va y Ven, mientras se exporta la capa del Geoportal |
| 5. Llegar del transporte al negocio | Solicitud de datos | 5.1 Tren Maya: pasajeros por mes | real | 122 registros mensuales, de dic 2023 a 2026 |
| | | 5.2 ATY: ruta R901 La Plancha – Teya | real | Horario, tarifas, 10 paradas y trazo |
| | | 5.3 Ayuntamiento de Mérida: obras de banquetas | real (sustituto) | 101 obras de banquetas 2023-2026 del SRFT, con ubicación |
| 6. Los últimos metros a pie | LiDAR | 6.1, 6.2 y 6.3: tramos de banqueta | simulado | Mediciones de 3 tramos de la calle 59 y una nube de puntos (.ply) por tramo |
| 7. Encontrar un negocio no siempre significa poder entrar | Realidad aumentada | 7.1, 7.2 y 7.3: entradas de negocios | simulado | Prueba de la silla de ruedas virtual en la entrada de 3 restaurantes del recorrido |
| 8. Permanecer también importa | Autoproducidos | 8.1 Bancas, 8.2 Ocupación y 8.3 Entrevistas | simulado | 14 bancas, 18 conteos de ocupación y 18 entrevistas anónimas |
| 9. Hacer visibles las oportunidades | Scraping | 9.1 Sección Amarilla, restaurantes de Mérida | real | 400 negocios, 200 con coordenadas |
| | | 9.2 Tren Maya, horarios oficiales | real | 32 tramos de 23 circulaciones |
| | | 9.3 Guía de la estación Teya-Mérida | real | 202 tarifas desde Teya y 3 conexiones |

Sobre el subtema 5, «Solicitud de datos»: las tres solicitudes de acceso a la información se presentaron el 2026-11-25 en la Plataforma Nacional de Transparencia. Su texto, folio y fecha límite (23 y 24 de diciembre de 2026) están en [`campo/05_solicitud_datos/`](campo/05_solicitud_datos/). Mientras llega la respuesta, se usa el dato público del mismo tema, como marca la regla del proyecto: si no hay respuesta en 3 semanas, queda el dato público.

`src/generar_solicitudes.py` arma tablas con la forma y el detalle que pide cada solicitud, calibradas con los datos públicos; sus totales cuadran con ellos:

| Solicitud | Tablas (`datos/propios/05_solicitud_datos/`) | Calibradas con |
|---|---|---|
| 5.1 Tren Maya | Pasajeros por estación y mes; Teya por día de la semana y corrida; origen-destino con Teya; boletos por tarifa | Pasajeros y boletos mensuales de toda la red, horarios oficiales y tiempos de viaje desde Teya |
| 5.2 ATY, R901 | Corridas programadas y realizadas; validaciones por tarifa, por parada y sentido, y por corrida | Viajes, paradas y tarifas del GTFS y del IE-TRAM |
| 5.3 Ayuntamiento, banquetas del Centro | 32 obras de 2023 a 2026 con calle, cruzamientos, coordenadas, metros, rampas, montos, financiamiento y fechas | Costo por m² de las 101 obras del SRFT |

## Entregables

| Entregable | Archivo | Contenido |
|---|---|---|
| Catálogo de fuentes | [`fuentes.csv`](fuentes.csv) | Las 27 fuentes con tipo, URL, licencia, fecha de descarga y estado |
| Catálogo de tablas | [`catalogo_tablas.csv`](catalogo_tablas.csv) | Las 52 tablas (24 silver, 10 gold y 18 propias): clave, granularidad, cobertura temporal, territorio, fuente, unidad, versión de la fuente, formato, filas y responsable |
| Diccionario de columnas | [`diccionario_columnas.csv`](diccionario_columnas.csv) | 901 columnas con tipo, descripción, unidad, % de vacíos y origen de la definición (diccionarios oficiales del INEGI, CONAPO, GTFS, SRFT y OpenStreetMap) |
| Capítulo del booklet | [`booklet/`](booklet/) | Ficha del capítulo, 4 escenas en D3 con su título-hallazgo, sus datos y sus fuentes |
| Archivos curados | `datos/curados/` y `datos/gold/` | Parquet y CSV UTF-8 |
| Registros rechazados | `datos/rechazados/` | Un CSV por tabla con la regla y el motivo de cada rechazo |
| Reporte de calidad | [`reportes/calidad.md`](reportes/calidad.md) | Conciliación por tabla, rechazos, columnas con vacíos y cobertura. Detalle por columna en `reportes/calidad_columnas.csv` |
| Conciliación | [`reportes/conciliacion.csv`](reportes/conciliacion.csv) | Conteos del original, para ETL, curado y rechazados, y controles de totales de gold |
| Indicadores | [`datos/gold/indicadores.csv`](datos/gold/indicadores.csv) | Fórmula, numerador, denominador y unidad de cada indicador |
| Tablas staging | [`sql/staging.sql`](sql/staging.sql) y `src/cargar_staging.py` | Esquema `e8_staging` en PostgreSQL y su carga repetible e incremental |
| Scripts ETL | `src/` | Descarga, preparación, curado, gold, carga y validación |
| Manifiesto | [`manifest.csv`](manifest.csv) | Un renglón por archivo de datos de todas las capas, con SHA-256 y archivo del que deriva |

## Capas

| Capa | Carpeta | Qué se hace |
|---|---|---|
| bronze | `datos/originales/` | Se guarda el original sin editar y su `procedencia.json` (URL, parámetros, fecha UTC, bytes, SHA-256, licencia, versión). Los scripts no vuelven a bajar una versión que ya existe |
| preparación | `datos/para-etl/` | Se extrae la tabla del original (JSON, ZIP, PDF, HTML, GTFS) a CSV UTF-8, con claves del INEGI y coordenadas EPSG:4326 |
| silver | `datos/curados/` | `src/curar.py` corrige tipos, codificación y fechas, normaliza texto y aplica las reglas de calidad: duplicados, claves nulas o repetidas, coordenadas incompletas o fuera del área, valores negativos imposibles, y reglas propias de cada tabla. Lo rechazado va a `datos/rechazados/` |
| propio | `datos/propios/` | `src/generar_solicitudes.py` arma las tablas de las 3 solicitudes y, con `src/generar_campo.py`, las de campo. Cada tabla se comprueba contra el dato que la calibra o contra las reglas de `validar_campo.py` |
| gold | `datos/gold/` | `src/gold.py` arma las dimensiones compartidas (`dim_municipio`, `dim_ageb`, `dim_tiempo`, `dim_estacion`) y los indicadores. Cada indicador comprueba que sus totales cuadren con su entrada |
| staging | PostgreSQL `e8_staging` | `src/cargar_staging.py` carga silver, gold y propias. Solo recarga lo que cambió y compara el conteo en la base con el catálogo |

Indicadores de la capa gold:

| Tabla | Granularidad | Qué mide |
|---|---|---|
| `ind_negocios_ageb_merida` | AGEB urbana de Mérida | Establecimientos 2019 y 2025, por cada 1,000 habitantes, variación y marginación |
| `ind_municipio_contexto` | Municipio, 5 estados | Población 2020 y 2025, marginación, accesibilidad y establecimientos por cada 1,000 habitantes |
| `ind_tren_maya_mensual` | Mes | Pasajeros, boletos, kilómetros, pasajeros por km y variación anual |
| `ind_restaurantes_transporte` | Restaurante | Distancia a la parada de transporte público más cercana y paradas a 400 m |
| `ind_ageb_entorno_merida` | AGEB urbana de Mérida | Paradas, restaurantes, instalaciones deportivas, estacionamientos de bicicletas y km de ciclovía, con densidades y tasas por 10,000 habitantes |
| `ind_obras_banquetas_anual` | Año | Obras, m², monto aprobado y monto por m² |

Estado de los datos al 2026-11-24:

- **Conteos:** cuadran en las 24 tablas silver, en los 13 controles gold y en los 23 controles de las tablas propias.
- **Rechazos:** 5 de 55,052 registros. Son anuncios de Sección Amarilla que declaran otro municipio.
- **Cruces:** las 526 AGEB del indicador encuentran su dimensión, sin huérfanos.
- **Reproducibilidad:** al regenerar todo desde cero, los 254 archivos del manifiesto salen idénticos, byte por byte.

## Estructura

```
fuentes.csv               catálogo de las 27 fuentes
catalogo_tablas.csv       catálogo de las tablas curadas, gold y propias
diccionario_columnas.csv  diccionario de columnas
manifest.csv              un renglón por archivo de datos, con SHA-256
externos.csv              archivos que no van en git, con su motivo (tamaño, privacidad, derechos) y su SHA-256
LICENCIAS.md              licencia y forma de citar cada fuente
datos/
  originales/NN_tipo/N.M_fuente/   bronze: tal como se descargó; procedencia.json por fuente
  para-etl/NN_tipo/N.M_fuente/     tablas extraídas, CSV UTF-8 y GeoJSON EPSG:4326
  curados/NN_tipo/N.M_fuente/      silver: Parquet y CSV curados
  rechazados/                      registros rechazados, con regla y motivo
  gold/                            dimensiones, indicadores e indicadores.csv
  propios/                         tablas de las solicitudes (05) y de campo (06 a 08) generadas por el equipo
reportes/                          calidad.md, calidad_columnas.csv y conciliacion.csv
sql/staging.sql                    esquema staging para PostgreSQL
campo/RECORRIDO.md                 recorrido y puntos del levantamiento de campo
booklet/                           capítulo del booklet: ficha, datos y escenas en D3
campo/NN_tipo/N.M_fuente/          protocolos, plantillas y capturas propias (subtemas 6, 7 y 8)
campo/05_solicitud_datos/          solicitudes de acceso a la información y su seguimiento
procesamiento/03_denue_datamart/   data mart del DENUE: modelo estrella para PostgreSQL
src/                               scripts del pipeline
```

## Cómo reproducir

Requiere Python 3.12.

```bash
pip install -r requirements.txt

python src/pipeline.py               # preparación, silver, gold, propias, booklet, reporte, manifiesto y validación
python src/pipeline.py --descargar   # lo mismo, y antes baja los originales que falten
```

Para cargar a PostgreSQL, con las variables estándar `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` y `PGPASSWORD`:

```bash
python src/cargar_staging.py             # carga incremental en el esquema e8_staging
python src/cargar_staging.py --forzar    # recarga todo
python src/cargar_staging.py --solo-sql  # solo regenera sql/staging.sql
```

Scripts por etapa:

| Etapa | Script |
|---|---|
| Descarga | `01_05_datos_gob.py` (API CKAN de datos.gob.mx), `02_siegy.py`, `03_inegi.py`, `04_geoportal_merida.py` (incluye los sustitutos de OpenStreetMap para 4.1 y 4.2), `05_aty_ruta_r901.py`, `05_ayuntamiento_banquetas.py` y `scraping/9.x_*.py` |
| Preparación | `para_etl_01_03_05.py`; las demás fuentes se preparan en su script de descarga |
| Silver | `curar.py`, con la especificación de cada tabla en `tablas.py` y las descripciones en `descripciones.csv` |
| Gold | `gold.py` |
| Propias | `generar_solicitudes.py` (solicitudes) y `generar_campo.py` (campo), con semilla fija: reproducen los mismos archivos |
| Booklet | `booklet.py`: datos de las 4 escenas, copia para abrir sin servidor y una página por escena |
| Territorio | `ageb.py`: asigna la AGEB urbana a cualquier punto con los polígonos del Marco Geoestadístico |
| Control | `reporte_calidad.py`, `generar_manifest.py`, `validar_entrega.py` (sirve para cualquier equipo: `--raiz` y `--equipo`) y `validar_campo.py` |
| Carga | `cargar_staging.py` |
| Campo | `generar_modelo_silla.py` (modelo de la silla de ruedas para la realidad aumentada) |

El data mart del subtema 3 se corre aparte; los pasos están en [su README](procesamiento/03_denue_datamart/README.md). Con los ZIP de este repositorio, ese pipeline reproduce el data mart sin diferencias.

## Claves para el ETL

- **Territorio:** las claves del INEGI van como texto, con ceros a la izquierda: `cvegeo_mun` (5 caracteres), `cvegeo_loc` (9) y `cvegeo_ageb` (13). Con ellas se cruzan CONAPO, el Censo, el DENUE y las capturas de campo, y también las dimensiones `dim_municipio` y `dim_ageb`. Las 1,220 AGEB de CONAPO están todas en el Censo. Para unir tablas hay que usar las `cvegeo_*`: las columnas de origen como `cve_mun` o `clave` no traen los ceros a la izquierda.
- **Coordenadas:** van en grados decimales, WGS84 (EPSG:4326), en las columnas `lat` y `lon`.
- **Fechas:** en formato ISO 8601. En los originales, la fecha de descarga está en UTC.
- **Alcance:** los 5 estados del Tren Maya (Campeche 04, Chiapas 07, Quintana Roo 23, Tabasco 27 y Yucatán 31) a nivel municipal, y Yucatán a nivel AGEB y localidad.
- **Precauciones por fuente:**
  - **SIEGY:** cada indicador conserva su periodo y su territorio. Un valor estatal se cuenta una sola vez.
  - **Tren Maya (5.1):** los datos reales son de toda la red, no por estación. El dato por estación es el que pide la solicitud 5.1; su tabla está en `datos/propios/`.
  - **Sección Amarilla:** en silver se rechazan 5 anuncios que declaran otro municipio. A los que no traen municipio se les asigna Mérida y quedan marcados en `municipio_imputado`. `colonia_normalizada` agrupa variantes como «CENTRO» y «MERIDA CENTRO».
  - **SRFT (5.3):** ninguna de las 101 obras está en el Centro Histórico. El dato del Centro es el que pide la solicitud 5.3; su tabla está en `datos/propios/`.
  - **OpenStreetMap (4.2):** `categoria` separa ciclovías, carriles en calle y estacionamientos. Para medir kilómetros, sumar `longitud_m` solo de ciclovías y carriles. Es un sustituto: describe la red ciclista, no el Circuito Enlace.
  - **OpenStreetMap (4.1):** incluye canchas de escuelas, clubes y fraccionamientos, no solo las unidades del Ayuntamiento. `acceso_publico_probable` separa las que tienen acceso restringido. La licencia ODbL pide atribución y compartir con la misma licencia las bases que se deriven.
  - **CONAPO, indicadores demográficos:** las notas oficiales de `ind_env_60`, `ind_env_65` y `raz_dep_adu` no cuadran con los datos. El diccionario trae la definición que sí cuadra y lo indica.
- **Campo:** las tablas del levantamiento llevan fecha, hora, `lat`, `lon` y `cvegeo_ageb`.
- **AGEB de un punto:** `src/ageb.py` asigna la `cvegeo_ageb` con los polígonos del Marco Geoestadístico 2025 (`datos/para-etl/03_inegi/3.3_censo_2020_ageb/ageb_urbana_yucatan_poligonos.geojson`). Coincide en 99.9 % con la AGEB que el propio DENUE asigna a cada negocio.

## Pendientes del equipo

| Qué | Quién | Cómo |
|---|---|---|
| Exportar las capas 4.1, 4.2 y 4.3 del Geoportal (opcional: las tres ya tienen sustituto) | Cualquier integrante, desde el navegador | Los pasos están en el `PENDIENTE.md` de cada carpeta. Después: `python src/04_geoportal_merida.py`, cambiar el estado en `fuentes.csv` y agregar la tabla en `src/tablas.py` |
| Dar seguimiento a las 3 solicitudes | Quien las presentó (2026-11-25), en la Plataforma Nacional de Transparencia | Folios y fechas límite en la tabla de seguimiento de cada `campo/05_solicitud_datos/*/solicitud.md`. Falta guardar el acuse en PDF de cada una como `acuse.pdf`. Al llegar la respuesta, guardarla como `respuesta.<ext>` |
| Levantamiento en campo de LiDAR, AR y bancas (opcional) | Equipo en campo | Recorrido, puntos y lista de lo que hay que llevar en [`campo/RECORRIDO.md`](campo/RECORRIDO.md). Protocolos en cada carpeta de `campo/`. Modelo de la silla para la realidad aumentada en `campo/07_ar_entradas/modelo/`. Al terminar: `python src/validar_campo.py` |

Antes de subir cualquier cambio:

```bash
python src/pipeline.py
```

Las fotos y los videos se suben con caras y placas difuminadas. Las entrevistas no llevan nombres, teléfonos ni correos.
