# 4.1 Unidades deportivas: exportación manual pendiente

Capa: https://geoportal.merida.gob.mx/unidadesdeportivas (Geoportal del Ayuntamiento de Mérida).

## Por qué no se descarga con script

- Toda petición automatizada a `geoportal.merida.gob.mx` redirige (HTTP 302) a una verificación antibots con captcha (`validate.perfdrive.com`). La última comprobación queda en `procedencia.json` (`comprobacion_acceso`).
- `robots.txt` del Geoportal prohíbe `/geoapijs`, `/vistas` y `/embed/` a clientes automatizados.
- No se encontró la misma capa en datos.gob.mx, en un portal de datos abiertos del Ayuntamiento ni como servicio WFS o ArcGIS público. El portal `www.merida.gob.mx` tiene el mismo antibots.

Por eso la exporta una persona desde su navegador. No se usan scripts, extensiones ni servicios para saltar la verificación.

## Pasos (10 minutos)

1. Abre https://geoportal.merida.gob.mx/unidadesdeportivas en Chrome o Firefox, en una ventana normal. Si aparece la verificación, resuélvela tú.
2. Espera a que cargue el mapa con los puntos de las unidades deportivas.
3. Busca la opción de descarga de la capa: el botón o icono **Descargar** (flecha hacia abajo) en el panel de capas o en la ficha de la capa. Elige, en este orden de preferencia:
   1. **KML** (siempre viene en WGS84).
   2. **GeoJSON** en WGS84 / EPSG:4326.
   3. **Shapefile (SHP)**: si es la única opción, ábrelo en QGIS y usa *Exportar > Guardar objetos como… > GeoJSON*, SRC **EPSG:4326**.
4. Si el Geoportal no ofrece botón de descarga:
   1. Abre la tabla o lista de la capa (icono de tabla o «Ver lista») y usa **Exportar a CSV/Excel** si existe; el CSV debe traer latitud y longitud.
   2. Si tampoco existe, abre las herramientas de desarrollador (F12), pestaña **Red** (Network), filtra por `Fetch/XHR`, recarga la página y busca la respuesta que trae los puntos (JSON con coordenadas). Clic derecho sobre ella > **Guardar respuesta como…** con extensión `.geojson` o `.json`.
5. Guarda el archivo con este nombre exacto en esta carpeta:
   `datos/originales/04_geoportal_merida/4.1_unidades_deportivas/unidades_deportivas_geoportal.kml` (o `.geojson`).
6. Anota en este archivo, al final, la fecha y el texto de licencia o términos que muestre el Geoportal (pie de página, «Acerca de» o la ficha de la capa).
7. Corre `python src/04_geoportal_merida.py`. El script registra el archivo en `procedencia.json` (sha256 y fecha UTC), cambia el estado a `real` y genera:
   - `datos/para-etl/04_geoportal_merida/4.1_unidades_deportivas/unidades_deportivas.geojson` (EPSG:4326)
   - `datos/para-etl/04_geoportal_merida/4.1_unidades_deportivas/unidades_deportivas.csv` (lat/lon)

Si las coordenadas no están en WGS84 el script se detiene y lo indica.

## Si no se puede exportar

- Pedir la capa por la Plataforma Nacional de Transparencia al **Ayuntamiento de Mérida** (Dirección de Desarrollo Urbano o Instituto Municipal del Deporte): «relación de unidades deportivas municipales con nombre, dirección, latitud y longitud, en formato CSV o KML».
- Sustituto público más cercano, **no equivalente** y por eso no se generó: el DENUE de mayo de 2025 que ya está en `datos/originales/03_inegi/3.2_denue_2025_05/denue_31_0525_csv.zip`, filtrando municipio `050` y las clases SCIAN 713942 (clubes deportivos del sector público), 713944 (centros de acondicionamiento físico del sector público) y 713999 (otros servicios recreativos del sector público). Da unas 18 unidades, muchas menos que las del Ayuntamiento, porque el DENUE registra establecimientos y no todos los campos y canchas públicas.

## Registro de la exportación

- Fecha:
- Formato descargado:
- Licencia o términos mostrados por el Geoportal:
