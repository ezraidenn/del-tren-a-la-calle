# Solicitud de acceso a la información: ATY, ruta R901 IE-TRAM y rutas que llegan a Teya

Borrador para presentar en la Plataforma Nacional de Transparencia (https://www.plataformadetransparencia.org.mx/), opción «Solicitudes de información» > «Información pública».

## Sujeto obligado

- Ámbito: Estatal, entidad federativa **Yucatán**.
- Sujeto obligado: **Agencia de Transporte de Yucatán (ATY)**.

## Texto de la solicitud

> Solicito, en formato abierto (CSV o XLSX), la siguiente información de la ruta R901 IE-TRAM «La Plancha – Estación Tren Maya Teya» y de cualquier otra ruta del Sistema Va-y-Ven o del IE-TRAM que tenga o haya tenido parada en la Estación Teya-Mérida del Tren Maya o en un radio de 1 km de ella, desde el inicio de operación de cada ruta hasta el último mes disponible:
>
> 1. Catálogo de paradas de cada ruta, en orden y por sentido, con identificador, nombre, latitud y longitud.
> 2. Trazo del recorrido de cada ruta por sentido (KML, GeoJSON o shapefile).
> 3. Horarios y frecuencias programados por tipo de día (lunes a viernes, sábado, domingo) y su vigencia, y número de corridas realizadas por mes.
> 4. Aforo: número de validaciones o pasajeros transportados por mes y por ruta; y, para la R901, por parada y sentido (ascensos y descensos) y por franja horaria, si se registra.
> 5. Tarifas vigentes por tipo de usuario y número de validaciones por mes y por tipo de tarifa en la R901.
> 6. Diccionario de datos o descripción de los campos y fecha de corte.
>
> La información se pide de forma agregada y estadística; no se solicita ningún dato personal ni información de tarjetas individuales. Si alguna parte no existe con ese nivel de detalle, solicito la desagregación más cercana que obre en sus archivos.

## Modalidad de entrega

- Modalidad: **Electrónica a través de la Plataforma Nacional de Transparencia**.
- Formato: **abierto, CSV o XLSX** (KML, GeoJSON o shapefile para los trazos).

## Notas para quien la presenta

- La PNT permite usar un nombre o seudónimo. El correo de notificaciones es el de la cuenta de quien presenta, no se escribe en este archivo.
- Guarda el acuse en PDF en esta carpeta como `acuse.pdf` y la respuesta como `respuesta.<ext>`.
- Dato público que se usa mientras tanto: paradas, trazo, viajes programados y tarifas de la R901 en `datos/para-etl/05_solicitud_datos/5.2_aty_ruta_r901/` (GTFS oficial de la ATY y página del IE-TRAM). En el GTFS vigente (versión 12.1), la única parada a 1 km o menos de la estación es «Estación Teya» y solo la atiende la R901. El aforo no es público: solo se puede obtener con esta solicitud.

## Respuesta simulada mientras tanto

En [`datos/simulados/05_solicitud_datos/5.2_aty_ruta_r901/`](../../../datos/simulados/05_solicitud_datos/5.2_aty_ruta_r901/) hay una respuesta **simulada** con la forma que pide esta solicitud: corridas programadas y realizadas, y validaciones por tarifa, por parada y sentido, y por corrida. Está calibrada con los datos públicos y marcada como simulada en cada archivo, tabla y renglón. El método está en su `LEEME_SIMULADO.md`. No es un dato oficial y no sustituye a la presentación de la solicitud. Cuando llegue la respuesta real, se guarda aquí y se dejan de usar las tablas simuladas.

## Regla del proyecto

Si en **3 semanas** desde la fecha de presentación no hay respuesta útil, el análisis usa el dato público que ya está en `datos/` y la solicitud se reporta como «presentada, sin respuesta a tiempo». Si la respuesta llega después, se agrega como fuente complementaria.

## Seguimiento

| Campo | Valor |
|---|---|
| Folio | 1163168926000225 |
| Fecha de presentación | 2026-11-25 (estatus en la PNT: en proceso) |
| Fecha límite de respuesta (20 días hábiles; verificar en el acuse) | 2026-12-24, según la PNT |
| Fecha límite de la regla del proyecto (3 semanas) | 2026-12-16 |
| Prórroga notificada (sí/no, nueva fecha) | |
| Respuesta (fecha y resumen) | |
| Archivos recibidos | |
| ¿Se usó en el análisis? | Todavía no. Mientras tanto se usan el dato público y la respuesta simulada |
