# Del tren a la calle

**¿Qué tan al alcance están las oportunidades alrededor del Tren Maya?**

Equipo: Raúl Cetina, Ricardo Horta, Damián Novelo. Grupo 9B, Ingeniería de Datos, UPY.

Este repositorio reúne las 27 fuentes del equipo: 9 subtemas, un tipo de fuente por subtema y 3 fuentes por tipo. Para cada fuente hay:

- el archivo original, tal como se descargó;
- su procedencia: URL, fecha UTC y SHA-256;
- una versión limpia lista para el ETL;
- el script que la reproduce.

[Fuentes](#fuentes) · [Estructura](#estructura) · [Cómo reproducir](#cómo-reproducir) · [Claves para el ETL](#claves-para-el-etl) · [Pendientes del equipo](#pendientes-del-equipo) · [Licencias](LICENCIAS.md)

## Fuentes

Estado al 2026-11-24: **16 reales** y **11 pendientes** (9 de levantamiento en campo y 2 capas del Geoportal). Ninguna es simulada. El catálogo completo, con licencia y fecha de descarga, está en [`fuentes.csv`](fuentes.csv).

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
| | | 3.3 Censo 2020 por AGEB y manzana urbana | real | 1,532 AGEB urbanas de Yucatán |
| 4. Una ciudad preparada para recibirlos | Geoportal de Mérida | 4.1 Unidades deportivas | pendiente | Exportación manual ([pasos](datos/originales/04_geoportal_merida/4.1_unidades_deportivas/PENDIENTE.md)) |
| | | 4.2 Circuito Enlace | pendiente | Exportación manual ([pasos](datos/originales/04_geoportal_merida/4.2_circuito_enlace/PENDIENTE.md)) |
| | | 4.3 Paraderos de transporte público | real (sustituto) | 3,256 paradas del GTFS oficial del Va y Ven, mientras se exporta la capa del Geoportal |
| 5. Llegar del transporte al negocio | Solicitud de datos | 5.1 Tren Maya: pasajeros por mes | real | 122 registros mensuales, de dic 2023 a 2026 |
| | | 5.2 ATY: ruta R901 La Plancha – Teya | real | Horario, tarifas, 10 paradas y trazo |
| | | 5.3 Ayuntamiento de Mérida: obras de banquetas | real (sustituto) | 101 obras de banquetas 2023-2026 del SRFT, con ubicación |
| 6. Los últimos metros a pie | LiDAR | 6.1, 6.2 y 6.3: tramos de banqueta | pendiente | Protocolo y plantilla en `campo/06_lidar_banquetas/` |
| 7. Encontrar un negocio no siempre significa poder entrar | Realidad aumentada | 7.1, 7.2 y 7.3: entradas de negocios | pendiente | Protocolo y plantilla en `campo/07_ar_entradas/` |
| 8. Permanecer también importa | Autoproducidos | 8.1 Bancas, 8.2 Ocupación y 8.3 Entrevistas | pendiente | Protocolo y plantilla en `campo/08_autoproducidos_permanencia/` |
| 9. Hacer visibles las oportunidades | Scraping | 9.1 Sección Amarilla, restaurantes de Mérida | real | 400 negocios, 200 con coordenadas |
| | | 9.2 Tren Maya, horarios oficiales | real | 32 tramos de 23 circulaciones |
| | | 9.3 Guía de la estación Teya-Mérida | real | 202 tarifas desde Teya y 3 conexiones |

Sobre el subtema 5, «Solicitud de datos»: las tres solicitudes de acceso a la información están redactadas en [`campo/05_solicitud_datos/`](campo/05_solicitud_datos/). Mientras llega la respuesta, se usa el dato público del mismo tema, como marca la regla del proyecto: si no hay respuesta en 3 semanas, queda el dato público.

## Estructura

```
fuentes.csv          catálogo de las 27 fuentes (id, subtema, tipo, URL, licencia, fecha, estado, carpeta)
manifest.csv         un renglón por archivo: bytes, SHA-256, URL o archivo del que deriva
externos.csv         archivos que no van en git, con su motivo (tamaño, privacidad, derechos) y su SHA-256
LICENCIAS.md         licencia y forma de citar cada fuente
datos/
  originales/NN_tipo/N.M_fuente/   tal como se descargó, nunca se edita; procedencia.json por fuente
  para-etl/NN_tipo/N.M_fuente/     CSV UTF-8 y GeoJSON EPSG:4326, listos para cargar
campo/NN_tipo/N.M_fuente/          protocolos, plantillas y capturas propias (subtemas 6, 7 y 8)
campo/05_solicitud_datos/          solicitudes de acceso a la información y su seguimiento
procesamiento/03_denue_datamart/   data mart del DENUE: modelo estrella para PostgreSQL
src/                               scripts de descarga, preparación y validación
```

## Cómo reproducir

Requiere Python 3.12.

```bash
pip install -r requirements.txt

# Descarga de originales
python src/01_05_datos_gob.py                 # subtema 1 y fuente 5.1, API CKAN de datos.gob.mx
python src/02_siegy.py                        # subtema 2, PDF e indicadores
python src/03_inegi.py                        # subtema 3, ZIP del INEGI
python src/04_geoportal_merida.py             # subtema 4, GTFS de la ATY y capas exportadas
python src/05_aty_ruta_r901.py                # fuente 5.2
python src/05_ayuntamiento_banquetas.py       # fuente 5.3
python src/scraping/9.1_seccion_amarilla_restaurantes.py
python src/scraping/9.2_tren_maya_horarios.py
python src/scraping/9.3_guia_estacion_teya.py

# Preparación y control
python src/para_etl_01_03_05.py               # CSV para el ETL de los subtemas 1, 3.3 y 5.1
python src/generar_manifest.py                # manifest.csv y externos.csv
python src/validar_entrega.py                 # reglas de aceptación del servidor
python src/validar_campo.py                   # capturas de campo
```

Los scripts no vuelven a bajar lo que ya existe. El data mart del subtema 3 se corre aparte; los pasos están en [su README](procesamiento/03_denue_datamart/README.md). Con los ZIP de este repositorio, ese pipeline reproduce el data mart sin diferencias.

## Claves para el ETL

- **Territorio:** las claves del INEGI van como texto, con ceros a la izquierda: `cvegeo_mun` (5 caracteres), `cvegeo_loc` (9) y `cvegeo_ageb` (13). Con ellas se cruzan CONAPO, el Censo, el DENUE y las capturas de campo. Las 1,220 AGEB de CONAPO están todas en el Censo.
- **Coordenadas:** van en grados decimales, WGS84 (EPSG:4326), en las columnas `lat` y `lon`.
- **Fechas:** en formato ISO 8601. En los originales, la fecha de descarga está en UTC.
- **Alcance:** los 5 estados del Tren Maya (Campeche 04, Chiapas 07, Quintana Roo 23, Tabasco 27 y Yucatán 31) a nivel municipal, y Yucatán a nivel AGEB y localidad.
- **Precauciones por fuente:**
  - **SIEGY:** cada indicador conserva su periodo y su territorio. Un valor estatal se cuenta una sola vez.
  - **Tren Maya (5.1):** los datos son de toda la red, no por estación. El dato por estación es el que pide la solicitud 5.1.
  - **Sección Amarilla:** 17 anuncios están fuera de Mérida o sin dirección. Las colonias no están normalizadas: aparecen «CENTRO» y «MERIDA CENTRO» por separado.
  - **SRFT (5.3):** ninguna de las 101 obras está en el Centro Histórico. El dato del Centro es el que pide la solicitud 5.3.
- **Campo:** las tablas del levantamiento llevan fecha, hora, `lat`, `lon` y `cvegeo_ageb`.

## Pendientes del equipo

| Qué | Quién | Cómo |
|---|---|---|
| Exportar las capas 4.1 y 4.2 del Geoportal | Cualquier integrante, desde el navegador | Los pasos están en el `PENDIENTE.md` de cada carpeta. Después: `python src/04_geoportal_merida.py` y cambiar el estado en `fuentes.csv` |
| Presentar las 3 solicitudes | Cualquier integrante, en la Plataforma Nacional de Transparencia | Texto listo en `campo/05_solicitud_datos/*/solicitud.md`. Guardar el acuse y llenar la tabla de seguimiento |
| Levantamiento LiDAR, AR y bancas (9 fuentes) | Equipo en campo | Protocolos en `campo/`. Al terminar: `python src/validar_campo.py` |

Antes de subir cualquier cambio:

```bash
python src/generar_manifest.py
python src/validar_entrega.py
```

Las fotos y los videos se suben con caras y placas difuminadas. Las entrevistas no llevan nombres, teléfonos ni correos.
