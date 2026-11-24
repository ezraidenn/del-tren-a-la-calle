# 4.3 Paraderos: se usa un sustituto; la capa original sigue pendiente

Capa original: https://geoportal.merida.gob.mx/paraderos (Geoportal del Ayuntamiento de Mérida). Toda petición automatizada redirige (HTTP 302) a una verificación antibots con captcha, y `robots.txt` prohíbe `/geoapijs`, `/vistas` y `/embed/`. No se rodea.

## Sustituto en uso

`gtfs_va_y_ven_aty.zip`: GTFS oficial del Sistema Va-y-Ven publicado por la Agencia de Transporte de Yucatán (ATY). Su `stops.txt` trae las 3,256 paradas de la red de transporte público de Mérida y su zona metropolitana con latitud y longitud. Lo enlaza el menú «GTFS» de https://transporteyucatan.org.mx/ y está registrado como feed oficial en Mobility Database (`mdb-3650`).

- Descarga: https://transit-scheduler.com/api/export-gtfs/latest (productor del feed).
- Espejo idéntico: https://files.mobilitydatabase.org/mdb-3650/latest.zip
- Salidas: `datos/para-etl/04_geoportal_merida/4.3_paraderos/paraderos_aty.csv` y `paraderos_aty.geojson`.

Diferencia con la capa del Geoportal: el GTFS lista los puntos donde se detienen las rutas; la capa municipal puede describir la infraestructura del paradero (techo, banca). Para el análisis de cercanía al transporte, el GTFS es la fuente operativa.

## Para tener también la capa original

1. Abre https://geoportal.merida.gob.mx/paraderos en tu navegador y resuelve tú la verificación si aparece.
2. Descarga la capa con el botón **Descargar** en **KML** o **GeoJSON EPSG:4326** (si solo hay SHP, conviértelo en QGIS a GeoJSON EPSG:4326). Si no hay botón, F12 > **Red** > `Fetch/XHR` > guarda la respuesta con los puntos.
3. Guárdala como `datos/originales/04_geoportal_merida/4.3_paraderos/paraderos_geoportal.kml` (o `.geojson`).
4. Corre `python src/04_geoportal_merida.py`: la registra en `procedencia.json` y genera `datos/para-etl/04_geoportal_merida/4.3_paraderos/paraderos_geoportal.geojson` y `.csv`.
