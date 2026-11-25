# 5.2 ATY, ruta R901: respuesta SIMULADA

**Estos datos son simulados. No son datos oficiales de la Agencia de Transporte de Yucatán.** Representan la respuesta que se espera a la solicitud de [`campo/05_solicitud_datos/5.2_aty_ruta_r901/solicitud.md`](../../../../campo/05_solicitud_datos/5.2_aty_ruta_r901/solicitud.md). Cuando llegue la respuesta real, la reemplaza.

Se generan con `python src/simular_solicitudes.py`, con semilla fija.

| Archivo | Responde al punto | Calibración con datos reales |
|---|---|---|
| `SIMULADO_r901_corridas_mes` | 3. Corridas programadas y realizadas por mes | Programadas = viajes del GTFS oficial por tipo de día × días del mes. Se pierde alrededor del 1.2 % de las corridas |
| `SIMULADO_r901_validaciones_tarifa` | 4 y 5. Aforo mensual por tipo de tarifa | Las tarifas son las publicadas por el IE-TRAM. Ingreso = validaciones × tarifa |
| `SIMULADO_r901_parada_sentido` | 4. Ascensos y descensos por parada y sentido | Paradas y orden del GTFS. En cada sentido, ascensos = descensos y nadie baja antes de subir |
| `SIMULADO_r901_validaciones_corrida` | 4. Validaciones por corrida (franja horaria) | Corridas del GTFS (trip_id y hora). Hacia Teya, la hora pico es en la mañana; desde Teya, a mediodía |

Supuestos de la simulación:

- **Periodo:** desde el inicio de la vigencia del GTFS (enero de 2026) hasta el último mes con pasajeros del Tren Maya.
- **Aforo:** el 8.5 % de los pasajeros que suben o bajan en Teya (tabla simulada 5.1) usa la R901. Se suman 38 viajes diarios entre paradas urbanas.
- **Mezcla de tarifas:**

  | Tipo de usuario | Participación |
  |---|---|
  | Turistas | 36 % |
  | General | 42 % |
  | Estudiantes y adultos mayores | 17 % |
  | Personas con discapacidad | 5 % |

Todas las tablas llevan `origen_dato = SIMULADO` y el id de fuente `E8-05.2-SIM`.
