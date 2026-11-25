# 4.2 Circuito Enlace: se usa un sustituto; la capa original sigue pendiente

## Sustituto en uso

`osm_infraestructura_ciclista.json`: respuesta de la API Overpass de OpenStreetMap con la infraestructura ciclista dentro del límite municipal de Mérida (relación 5961522). Incluye ciclovías, carriles en calle, estacionamientos y renta de bicicletas. La consulta exacta está en la URL registrada en `procedencia.json`.

- Salidas: `datos/para-etl/04_geoportal_merida/4.2_circuito_enlace/infraestructura_ciclista_osm.csv` y `.geojson`. Los tramos son líneas con su longitud y los estacionamientos son puntos.
- Licencia: ODbL 1.0, con atribución «© colaboradores de OpenStreetMap».
- Por qué este sustituto:
  - El recorrido del Circuito Enlace no se publica fuera del Geoportal. Se revisaron OpenStreetMap y las notas del Ayuntamiento y de la prensa de 2020 y 2022, y solo dan los nombres de las rutas.
  - En la consulta del 2026-11-25 el Geoportal mostró el mapa, pero sin descarga y sin respuestas con coordenadas.
  - La infraestructura ciclista es la otra red de movilidad urbana del subtema 4, distinta del GTFS que ya usa 4.3.
- No es equivalente: describe la red ciclista, no el transporte gratuito del Centro.

Si se consigue la capa original con los pasos de abajo, o digitalizándola desde el mapa del Geoportal, el script la convierte y la fuente pasa a usar la capa original.

Capa: https://geoportal.merida.gob.mx/circuitoenlace (Geoportal del Ayuntamiento de Mérida). Es el servicio gratuito de transporte del Centro que opera el Ayuntamiento, no la ATY.

## Por qué no se descarga con script

- Toda petición automatizada a `geoportal.merida.gob.mx` redirige (HTTP 302) a una verificación antibots con captcha (`validate.perfdrive.com`). La última comprobación queda en `procedencia.json` (`comprobacion_acceso`).
- `robots.txt` del Geoportal prohíbe `/geoapijs`, `/vistas` y `/embed/` a clientes automatizados.
- El GTFS oficial de la ATY (usado en 4.3 y 5.2) **no** incluye el Circuito Enlace: sus 174 rutas son del Sistema Va-y-Ven. Tampoco se encontró en datos.gob.mx ni en un portal de datos abiertos del Ayuntamiento. OpenStreetMap podría tener la ruta, pero su API pública (Overpass) no respondió durante la consulta y no se pudo confirmar.

Por eso la exporta una persona desde su navegador. No se usan scripts, extensiones ni servicios para saltar la verificación.

## Pasos (10 minutos)

1. Abre https://geoportal.merida.gob.mx/circuitoenlace en Chrome o Firefox, en una ventana normal. Si aparece la verificación, resuélvela tú.
2. Espera a que cargue el mapa con el recorrido y las paradas del circuito.
3. Busca el botón o icono **Descargar** en el panel de capas o en la ficha de la capa. Descarga **las dos capas** si vienen separadas (recorrido como línea y paradas como puntos). Formato, en este orden:
   1. **KML** (siempre viene en WGS84).
   2. **GeoJSON** en WGS84 / EPSG:4326.
   3. **Shapefile (SHP)**: ábrelo en QGIS y usa *Exportar > Guardar objetos como… > GeoJSON*, SRC **EPSG:4326**.
4. Si no hay botón de descarga, abre las herramientas de desarrollador (F12), pestaña **Red** (Network), filtra por `Fetch/XHR`, recarga la página y guarda la respuesta que trae el recorrido o las paradas (clic derecho > **Guardar respuesta como…**, extensión `.geojson` o `.json`).
5. Guarda los archivos con estos nombres en esta carpeta:
   - `datos/originales/04_geoportal_merida/4.2_circuito_enlace/circuito_enlace_recorrido.kml` (o `.geojson`)
   - `datos/originales/04_geoportal_merida/4.2_circuito_enlace/circuito_enlace_paradas.kml` (o `.geojson`)
6. Anota abajo la fecha, el horario publicado y el texto de licencia o términos que muestre el Geoportal.
7. Corre `python src/04_geoportal_merida.py`. El script registra los archivos en `procedencia.json` (sha256 y fecha UTC), cambia el estado a `real` y genera `datos/para-etl/04_geoportal_merida/4.2_circuito_enlace/circuito_enlace.geojson` (EPSG:4326, recorrido y paradas juntos; cada elemento trae `archivo_origen`).

## Si no se puede exportar

- Pedir por la Plataforma Nacional de Transparencia al **Ayuntamiento de Mérida** (Dirección de Gobernación o la unidad que opere el Circuito Enlace): «trazo del recorrido, ubicación de paradas, horario y frecuencia del Circuito Enlace, en KML o CSV con latitud y longitud».
- Sustituto parcial, **no equivalente**: las rutas del Va-y-Ven que pasan por el Centro en `datos/para-etl/04_geoportal_merida/4.3_paraderos/paraderos_aty.csv` (columna `rutas`). Sirven para medir cobertura de transporte en el Centro, no para describir el Circuito Enlace.

## Registro de la exportación

- Fecha:
- Formato descargado:
- Horario y frecuencia publicados:
- Licencia o términos mostrados por el Geoportal:
