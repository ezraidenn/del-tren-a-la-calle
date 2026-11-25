# Recorrido del levantamiento de campo

Las 9 fuentes de campo (subtemas 6, 7 y 8) se levantan sobre un mismo recorrido a pie, entre dos paradas de transporte público, con restaurantes en el camino.

Hoy las 9 están **simuladas** sobre este recorrido (ver [LEEME_SIMULADO.md](LEEME_SIMULADO.md)). Esta guía sirve para hacer el levantamiento real y reemplazarlas.

## Calle 62 de la 57 a la 59, y calle 59 de la 62 a la 58 (Centro)

| Punto | Parada del GTFS de la ATY | Cruce | Lat, lon | Rutas |
|---|---|---|---|---|
| Inicio | 950 «La Chaya Maya» | calle 62 x 57 | 20.970100, -89.624310 | 15 |
| Fin | 2792 «Palacio de la Música» | calle 58 x 59 | 20.969063, -89.621562 | 2 |

- **Largo:** unos 400 m a pie: una cuadra hacia el sur por la calle 62 y dos hacia el oriente por la calle 59.
- **Por qué este recorrido:** une la parada con más rutas del Centro con la zona que tiene más restaurantes de Sección Amarilla cerca de una parada: 14 a menos de 300 m.
- **Lugar para sentarse:** el recorrido pasa por el Parque Hidalgo (calle 60 x 59), que sirve para el inventario y la ocupación de bancas.
- **Coordenadas:** salen de `datos/para-etl/04_geoportal_merida/4.3_paraderos/paraderos_aty.csv`.

## Qué se levanta en cada punto

| Fuente | Dónde | Sugerencia |
|---|---|---|
| 6.1 Tramo 1 | Calle 59, entre 62 y 60 | Un tramo en buen estado, como referencia |
| 6.2 Tramo 2 | Calle 59, entre 60 y 58 | Un tramo con un obstáculo: poste, árbol, puesto o mesas |
| 6.3 Tramo 3 | Esquina de la calle 59 con la 60, junto al Parque Hidalgo | Un tramo con desnivel o rampa de esquina |
| 7.1 Entrada 1 | La Chaya Maya, calle 62 x 57 (20.970049, -89.624031) | Restaurante junto a la parada de inicio |
| 7.2 Entrada 2 | Café Rollal (20.969910, -89.623780) | A media cuadra del recorrido, según Sección Amarilla; confirmar la dirección en el lugar |
| 7.3 Entrada 3 | El Chile Habanero (20.970238, -89.622520) | Si no se puede, usar de reserva el Patio Bar Pancho's (20.968684, -89.623160) |
| 8.1 Bancas | Todas las bancas del recorrido y del Parque Hidalgo | Incluir también escalones o jardineras que la gente use para sentarse |
| 8.2 Ocupación | Las bancas del inventario más cercanas a las dos paradas | Tres franjas: 8 a 9, 13 a 14 y 18 a 19 |
| 8.3 Entrevistas | En las dos paradas y en el Parque Hidalgo | De 15 a 20 personas que esperan o descansan |

Las ubicaciones de los negocios salen de Sección Amarilla (fuente 9.1). Hay que confirmarlas en el lugar: si un negocio ya no está o no da permiso, se usa el siguiente sobre el recorrido y se anota en `observaciones`.

## Antes de salir

- Un iPhone o iPad Pro con LiDAR, con la 3d Scanner App y la app Medida.
- Un flexómetro.
- El modelo de la silla de ruedas abierto en el celular: [`07_ar_entradas/modelo/`](07_ar_entradas/modelo/).
- Las plantillas CSV de cada carpeta, en el celular o impresas.
- Pedir permiso al encargado de cada negocio antes de la prueba de realidad aumentada.
- No grabar caras, placas ni el interior de los negocios.

## Al terminar

```bash
python src/validar_campo.py
```

Revisa el formato de fechas y horas, que las coordenadas caigan en Mérida, los rangos de las mediciones, que existan los archivos que se citan y que no haya datos personales.
