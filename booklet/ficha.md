# CAPÍTULO 02 · DEL TREN A LA CALLE · ACTO 1: LLEGAN

Equipo 8: Damian, Raúl y Ricardo · Repositorio `ezraidenn/del-tren-a-la-calle`

---

## Título-hallazgo

**Llegó el tren y llegaron 5,488 negocios más a sus alrededores, pero en 2026 el tren lleva 7.8 % menos pasajeros**

## Pregunta del capítulo

¿Qué cambió alrededor de las estaciones del Tren Maya y, ya en Mérida, quién ganó negocios?

## Entrada

Entre 2019 y 2025 crecieron los negocios cerca de casi todas las estaciones, sobre todo de 1 a 3 km y no pegados a la vía. En Mérida crecieron las orillas y el Centro perdió negocios, mientras el tren, en 2026, lleva menos gente que un año antes.

Capítulo completo en D3: [`index.html`](index.html). Una página por escena en [`graficas/`](graficas/).

---

## La historia en 10 segundos

| Cifra | Qué es | Fuente y corte |
| :--- | :--- | :--- |
| **+5,488 negocios** | A 5 km de las 34 estaciones: de 39,350 en 2019 a 44,838 en 2025 (+13.9 %). | INEGI, DENUE nov 2019 y may 2025 (`datos/escena-2.csv`) |
| **−7.8 % pasajeros** | De enero a septiembre de 2026 el tren llevó 891,060 pasajeros, frente a 966,552 en el mismo periodo de 2025. | Tren Maya, datos.gob.mx, corte sep 2026 (`datos/escena-3.csv`) |
| **−507 negocios** | En la AGEB del Centro de Mérida (`3105000010510`), de 3,400 a 2,893, mientras 350 de las 526 AGEB urbanas ganaron negocios. | INEGI, DENUE y Censo 2020 (`datos/escena-4.csv`) |

En `index.html` estas tres cifras se calculan de los CSV (`graficas/portada.js`); no están escritas en el código.

---

## Escenas

### Escena 1 · Los negocios no se subieron al andén: +2,651 de 1 a 3 km de la estación y solo +484 a menos de 1 km

- **Subtítulo:** negocios del DENUE en tres anillos alrededor de las 34 estaciones del Tren Maya, noviembre de 2019 contra mayo de 2025. Cada negocio cuenta una sola vez, en la estación más cercana.
- **Datos:** [`datos/escena-1.csv`](datos/escena-1.csv) · **D3:** [`graficas/escena-1.html`](graficas/escena-1.html)
- **Lectura:** la estación va al centro y cada anillo es una distancia.
  - Dentro de cada anillo va lo que ganó; el morado es más intenso donde creció más.
  - A la derecha, cada anillo en 2019 (oro) y en 2025 (morado).
  - El anillo de 1 a 3 km creció +16.2 %. El de junto a la estación creció +12.7 % y el de 3 a 5 km, +12.3 %.
- **Fuente:** INEGI, DENUE noviembre 2019 y mayo 2025; catálogo de estaciones del Tren Maya. Data mart del equipo. Corte: mayo de 2025.

### Escena 2 · Tulum se llevó la vagonada, +900 negocios a 5 km de su estación, y Mérida Teya quedó tercera con +677

- **Subtítulo:** negocios ganados o perdidos a menos de 5 km de cada una de las 34 estaciones, de noviembre de 2019 a mayo de 2025.
- **Datos:** [`datos/escena-2.csv`](datos/escena-2.csv), [`datos/escena-2-anillos.csv`](datos/escena-2-anillos.csv) y [`datos/estados_tren_maya.geojson`](datos/estados_tren_maya.geojson) · **D3:** [`graficas/escena-2.html`](graficas/escena-2.html)
- **Lectura:** cada círculo es una estación en su lugar de la península, del tamaño de los negocios que ganó (morado) o perdió (oro) a 5 km.
  - El borde negro marca la estación cuyo detalle por anillo (2019 contra 2025) se ve a la derecha: Mérida Teya en el impreso; en pantalla, la que se toque.
  - Las que perdieron son Candelaria y Chetumal Aeropuerto.
  - La línea punteada une las estaciones en el orden de la ruta; no es el trazo real de la vía.
  - Palenque, segunda con +732, es la única estación de Chiapas: su cambio es el de todo el estado. Por eso no comparamos estados por su total.
- **Fuente:** igual que la escena 1; contorno de los estados: INEGI, Marco Geoestadístico (diciembre 2025). Corte: mayo de 2025.

### Escena 3 · En pleno calor, el tren se enfrió: de junio a septiembre de 2026 llevó entre 18 % y 28 % menos pasajeros que en 2025

- **Subtítulo:** pasajeros transportados por mes en toda la red, enero de 2025 a septiembre de 2026.
- **Datos:** [`datos/escena-3.csv`](datos/escena-3.csv) · **D3:** [`graficas/escena-3.html`](graficas/escena-3.html)
- **Lectura:** la línea oro es 2025 y la morada, 2026.
  - 2026 empezó arriba y desde junio quedó abajo.
  - Agosto tuvo la mayor caída (−27.7 %).
  - Septiembre de 2026, con 66,801 pasajeros, es el mes más bajo de la serie.
- **Fuente:** Tren Maya, prestación del servicio ferroviario de pasajeros, datos.gob.mx. Tabla gold `ind_tren_maya_mensual`. Corte: septiembre de 2026.

### Escena 4 · Los negocios agarraron pa' las orillas: 350 de 526 AGEB de Mérida ganaron negocios y la del Centro perdió 507

- **Subtítulo:** negocios ganados o perdidos en cada AGEB urbana del municipio de Mérida, de noviembre de 2019 a mayo de 2025.
- **Datos:** [`datos/escena-4.csv`](datos/escena-4.csv) y [`datos/merida_ageb.geojson`](datos/merida_ageb.geojson) · **D3:** [`graficas/escena-4.html`](graficas/escena-4.html)
- **Lectura:**
  - El municipio pasó de 52,675 a 55,864 negocios (+6.1 %).
  - El Centro bajó de 3,400 a 2,893 negocios (−14.9 %).
  - Las AGEB a más de 20 km de la estación Teya crecieron 47.6 %.
  - Es el indicador por AGEB que aportamos al mapa de síntesis del cierre.
- **Fuente:** INEGI, DENUE noviembre 2019 y mayo 2025, Censo 2020 y Marco Geoestadístico (diciembre 2025); CONAPO, índice de marginación urbana 2020. Tabla gold `ind_negocios_ageb_merida`. Corte: mayo de 2025.

---

## Lo que estos datos no dicen

1. **No prueban que el tren causó el cambio.** El DENUE de 2019 es anterior a la obra y el de mayo de 2025 llega año y medio después de la apertura (diciembre de 2023). En medio también hubo pandemia y crecimiento urbano.
2. **El DENUE cuenta establecimientos, no ventas ni empleos.**
3. **Los estados no se comparan por su total.** Chiapas solo tiene la estación de Palenque y Tabasco tiene tres, frente a las once de Campeche y las doce de Quintana Roo.
4. **Los pasajeros son de toda la red.** El dato por estación se pidió por transparencia (folio 343053500035426). La respuesta vence el 23 de diciembre de 2026.
5. **La estación Teya está en Kanasín,** a 6.4 km del centro de la AGEB urbana de Mérida más cercana. El mapa muestra cómo cambió la ciudad, no el efecto directo de la estación.
6. **La población por AGEB es la del Censo 2020.** Las 19 AGEB nuevas del Marco Geoestadístico 2025 aparecen en blanco.

## Puente al Acto 2

Llegaron el tren y miles de negocios nuevos; falta saber si a quien vive en Mérida le alcanza el sueldo para comprar en ellos.

---

## Fallas del repositorio (sección 6 del plan)

| Falla | Qué se hizo |
| :--- | :--- |
| El diseño era para Power BI, no había `.pbix` y las gráficas de `libro/graficas_e8.csv` solo estaban especificadas | Se hicieron las 4 escenas en D3 7.9.0 en `graficas/`. Leen los CSV de `datos/` y cada una lleva su título-hallazgo. `libro/` se retiró y la guía de Power BI del data mart quedó como alternativa |
| Datos simulados del campo y de las 3 solicitudes | No entran al booklet: las 4 escenas solo usan fuentes públicas. En el repositorio quedan en `datos/propios/`, con su aviso en el README. Las entrevistas ya no guardan coordenadas exactas: llevan el punto del recorrido donde se hicieron (banca o parada), a 4 decimales |
| Dos títulos («Del tren a la calle» y «El tren que movió el mapa») | Queda «Del tren a la calle» en todo el repositorio |
| Chiapas solo tiene la estación de Palenque | Se marca en la escena 2 y en «Lo que estos datos no dicen»; no se comparan estados por su total |

## Cómo se regenera y cómo se ve

```bash
python src/booklet.py            # escribe datos/ y graficas/escena-N.html
python -m http.server -d booklet # y abrir http://localhost:8000
```

Los títulos y las lecturas se editan en `index.html`; las páginas por escena se generan desde ahí.

Impreso en tamaño carta, el capítulo ocupa 5 páginas:
- la portada con la escena 1;
- una página para cada una de las escenas 2, 3 y 4;
- una para los límites y la frase puente.

Las gráficas van a todo lo ancho para que su texto no baje de 8 pt.

En pantalla, cada escena tiene una entrada animada que arranca al llegar a ella:
- **Escena 1:** los anillos se abren desde la estación.
- **Escena 2:** un tren recorre la ruta, cada estación aparece cuando pasa y el contador sube hasta +5,488. Al tocar una estación se ve su detalle por anillo.
- **Escena 3:** las líneas se dibujan mes a mes.
- **Escena 4:** Mérida se pinta del Centro hacia las orillas.

Con «reducir movimiento» activado, o al imprimir, las escenas aparecen ya terminadas.
