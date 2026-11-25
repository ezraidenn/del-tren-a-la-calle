# 5.3 Ayuntamiento de Mérida, banquetas del Centro: respuesta SIMULADA

**Estos datos son simulados. No son datos oficiales del Ayuntamiento de Mérida.** Representan la respuesta que se espera a la solicitud de [`campo/05_solicitud_datos/5.3_ayuntamiento_banquetas/solicitud.md`](../../../../campo/05_solicitud_datos/5.3_ayuntamiento_banquetas/solicitud.md). Cuando llegue la respuesta real, la reemplaza.

Se genera con `python src/simular_solicitudes.py`, con semilla fija.

`SIMULADO_obras_banquetas_centro` tiene una fila por obra, de 2023 a 2026, con los campos 1 a 6 que pide la solicitud: descripción, calle y cruzamientos, coordenadas, metros, rampas, montos, financiamiento, fechas, estatus y dependencia.

Calibración y supuestos:

- **Costo por m²:** parte de la mediana de las 101 obras de banquetas del Ayuntamiento en el SRFT de la SHCP (E8-05.3). Se multiplica por un factor según el tipo de acción, porque en el Centro se usa piedra y hay rampas y cruces. Cada rampa suma 14,500 pesos y cada cruce, 42,000.
- **Ubicación:** sigue la retícula de calles del Centro. Las pares corren de norte a sur y las impares de oriente a poniente, a partir de la Plaza Grande (calles 60, 61, 62 y 63). Las coordenadas son el punto medio del tramo.
- **Perímetro A y B:** aproximados por número de calle.
- **Obra de referencia:** la de la calle 52 entre 69 y 71 que menciona la solicitud está incluida. Se tomó de la nota de prensa del Ayuntamiento; sus montos y metros son simulados.
- **Identificadores:** son `SIM-OP-año-consecutivo`. No imitan números de contrato reales.

Lleva `origen_dato = SIMULADO` y el id de fuente `E8-05.3-SIM`.
