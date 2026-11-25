# 5.1 Tren Maya: respuesta SIMULADA

**Estos datos son simulados. No son datos oficiales de Tren Maya, S.A. de C.V.** Representan la respuesta que se espera a la solicitud de [`campo/05_solicitud_datos/5.1_tren_maya_pasajeros/solicitud.md`](../../../../campo/05_solicitud_datos/5.1_tren_maya_pasajeros/solicitud.md). Sirven para construir y probar el tablero mientras llega la respuesta real. Cuando llegue, la respuesta real reemplaza estas tablas.

Se generan con `python src/simular_solicitudes.py`, con semilla fija: cada corrida da los mismos archivos.

| Archivo | Responde al punto | Calibración con datos reales |
|---|---|---|
| `SIMULADO_tm_pasajeros_estacion_mes` | 1. Pasajeros por mes y estación, con ascensos y descensos | Cada mes, los ascensos de todas las estaciones suman exactamente los pasajeros transportados que publica datos.gob.mx (E8-05.1) |
| `SIMULADO_tm_teya_dia_corrida` | 2. Teya por día de la semana y corrida | Las corridas y sus horas salen de los horarios oficiales (E8-09.2). La suma cuadra con los ascensos y descensos de Teya |
| `SIMULADO_tm_origen_destino_teya` | 3. Pares origen-destino con Teya | Los destinos y tiempos de viaje salen de la guía de la estación Teya (E8-09.3). La suma cuadra con Teya |
| `SIMULADO_tm_boletos_tarifa` | 4. Boletos por tipo de tarifa | El total del sistema es igual a los boletos vendidos reales (pasajeros en los meses sin ese dato) |

Supuestos de la simulación:

- **Peso de cada estación:** las terminales aeroportuarias y las ciudades turísticas pesan más. Se aplica una variación aleatoria de alrededor del 10 % por mes.
- **Apertura por tramo:** Campeche a Cancún en diciembre de 2023; Playa del Carmen en febrero de 2024; Palenque y Tulum en marzo de 2024; Felipe Carrillo Puerto a Chetumal y Escárcega en diciembre de 2024. Antes de su apertura, una estación no tiene pasajeros.
- **Teya:** se usan los horarios vigentes en todos los meses. Viernes, sábado y domingo pesan más que entre semana.
- **Origen-destino:** un modelo de gravedad. El destino pesa según su estación y pesa menos mientras más largo es el viaje. Sin tiempo publicado (tramos 6 y 7), se suponen 5 horas.
- **Tarifas:** la parte internacional sube de diciembre a marzo.

Todas las tablas llevan la columna `origen_dato = SIMULADO`. En el catálogo van en la capa `simulado`, con el id de fuente `E8-05.1-SIM`.
