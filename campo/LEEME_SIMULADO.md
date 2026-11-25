# Levantamiento de campo SIMULADO

**Las 9 fuentes de campo (6.1 a 8.3) están simuladas. No son mediciones reales.** Se generaron con `src/simular_campo.py` sobre el recorrido de [RECORRIDO.md](RECORRIDO.md), con las mismas columnas de las plantillas de esta carpeta. Las plantillas siguen vacías, listas para un levantamiento real.

| Fuente | Archivos simulados | Qué trae |
|---|---|---|
| 6.1 a 6.3 LiDAR | `datos/simulados/06_lidar_banquetas/6.N_tramo_N/SIMULADO_mediciones.csv` y `SIMULADO_captura_TN.ply` | Ancho total y libre, obstáculos y pendiente de 3 tramos de la calle 59. La nube de puntos se construye con esas mismas medidas: fachada, banqueta, guarnición, arroyo, poste, registro y rampa, con ruido de 3 mm |
| 7.1 a 7.3 Realidad aumentada | `datos/simulados/07_ar_entradas/7.N_entrada_N/SIMULADO_registro.csv` | Prueba de la silla de ruedas virtual en 3 restaurantes de Sección Amarilla (fuente 9.1). Resultado según la regla de 0.80 m de paso y 2 cm de escalón |
| 8.1 Bancas | `datos/simulados/08_autoproducidos_permanencia/8.1_inventario_bancas/SIMULADO_inventario_bancas.csv` | 14 lugares para sentarse: confidentes y bancas del Parque Hidalgo, plazoleta del Palacio de la Música, parabús, y escalón y jardinera de la parada que no tiene banca |
| 8.2 Ocupación | `.../8.2_ocupacion_bancas/SIMULADO_conteo_ocupacion.csv` | 18 conteos de 15 minutos: 6 bancas en 3 franjas (mañana, mediodía y tarde) |
| 8.3 Entrevistas | `.../8.3_entrevistas/SIMULADO_respuestas.csv` | 18 entrevistas anónimas con el guion de 7 preguntas |

## Con qué se calibró

- **Coordenadas:** las de las paradas del GTFS de la ATY (4.3) y de los restaurantes de Sección Amarilla (9.1).
- **AGEB:** se asigna con los polígonos del Marco Geoestadístico del INEGI (3.3).
- **Medidas:** las típicas del Centro: banquetas de 1.2 a 1.4 m, postes de la red eléctrica sobre la banqueta, rampas de esquina con más del 8 % de pendiente, y accesos de casona con escalón de 17 a 24 cm.
- **Clima:** temperatura de fines de noviembre en Mérida, de 22 °C en la mañana a 31 °C a mediodía.

## Cómo se marca

- **Estado:** «simulado» en `fuentes.csv`.
- **Archivos:** prefijo `SIMULADO_` y columna `origen_dato = SIMULADO`.
- **Catálogo:** tablas `sim_campo_*` en la capa «simulado».
- **Nubes de puntos:** un comentario «SIMULADO» en la cabecera de cada `.ply`.
- **Sin fotos ni videos:** el campo de archivo de foto o video está vacío.

## Controles

Las filas simuladas pasan `src/validar_campo.py`, que revisa fechas, coordenadas en Mérida, AGEB del Censo, rangos de medida y datos personales. Además se comprueba que:
- el ancho libre no supere el ancho total;
- cada nube reproduzca el ancho medido con 1 cm de tolerancia;
- cada conteo corresponda a una banca del inventario.

Los resultados están en `reportes/conciliacion.csv`.

## Para reemplazarlas con un levantamiento real

1. Llenar las plantillas de `campo/` con el protocolo de cada carpeta.
2. Correr `python src/validar_campo.py`.
3. Cambiar en `fuentes.csv` el estado de la fuente a «real», con la fecha del levantamiento y `carpeta` apuntando a `campo/`.
4. Dejar de usar las tablas `sim_campo_*` de esa fuente.
