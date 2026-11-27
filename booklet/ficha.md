# Del tren a la calle
**Acto 3 · Moverse** · Equipo 8

---

## A 5 km de las 34 estaciones del Tren Maya hay 5,488 negocios más que en 2019, pero en 2026 el tren lleva 7.8 % menos pasajeros que en 2025

Comparamos los negocios del DENUE de noviembre de 2019 y de mayo de 2025 alrededor de cada estación, los pasajeros que publica el Tren Maya cada mes y, ya en Mérida, cómo cambió el número de negocios en cada AGEB urbana.

Capítulo completo en D3: [`index.html`](index.html). Una página por escena en [`graficas/`](graficas/).

---

## La historia en 10 segundos

| Dato clave | Descripción y contexto | Fuente y corte |
| :--- | :--- | :--- |
| **+5,488 negocios** | A 5 km de las 34 estaciones: de 39,350 en 2019 a 44,838 en 2025 (+13.9 %). | INEGI, DENUE nov 2019 y may 2025 (`escena-2.csv`) |
| **−7.8 % pasajeros** | De enero a septiembre de 2026 el tren llevó 891,060 pasajeros, frente a 966,552 en el mismo periodo de 2025. | Tren Maya, datos abiertos, corte sep 2026 (`escena-3.csv`) |
| **−507 negocios** | La AGEB del Centro de Mérida pasó de 3,400 a 2,893 negocios, mientras 350 de las 526 AGEB urbanas ganaron negocios. | INEGI, DENUE y Censo 2020 (`escena-4.csv`) |

---

## Escena 1 · El crecimiento no se quedó pegado a la vía: de 1 a 3 km de las estaciones se sumaron 2,651 negocios y a menos de 1 km, 484

- **Subtítulo:** negocios del DENUE en tres anillos alrededor de las 34 estaciones, noviembre de 2019 contra mayo de 2025. Cada negocio cuenta una sola vez, en la estación más cercana.
- **Archivo:** [`datos/escena-1.csv`](datos/escena-1.csv) · **Gráfica D3:** [`graficas/escena-1.html`](graficas/escena-1.html)
- **Cómo leer esta escena:**
  - Cada grupo de barras es un anillo de distancia; la barra gris es 2019 y la morada, 2025.
  - El anillo de 1 a 3 km creció +16.2 %. El de junto a la estación creció +12.7 % y el de 3 a 5 km, +12.3 %.
  - A menos de 1 km hay pocos negocios porque varias estaciones están fuera de la mancha urbana.
- **Fuente:** INEGI, DENUE noviembre 2019 y mayo 2025; catálogo de estaciones del Tren Maya. Data mart del equipo (`procesamiento/03_denue_datamart/`).

---

## Escena 2 · Tulum, Palenque y Mérida Teya sumaron 2,309 de los 5,488 negocios nuevos; Chetumal Aeropuerto y Candelaria perdieron

- **Subtítulo:** negocios ganados o perdidos a menos de 5 km de cada una de las 34 estaciones, de noviembre de 2019 a mayo de 2025.
- **Archivo:** [`datos/escena-2.csv`](datos/escena-2.csv) · **Gráfica D3:** [`graficas/escena-2.html`](graficas/escena-2.html)
- **Cómo leer esta escena:**
  - Las barras moradas son las estaciones que ganaron negocios y las de color oro, las que perdieron.
  - Tulum ganó 900 negocios (+53.7 %) y Mérida Teya, 677 (+48.6 %).
  - Edzná y Calakmul no tienen negocios registrados a 5 km.
  - **Palenque es la única estación de Chiapas**: su cambio (+732) es el de todo el estado. Por eso el capítulo no compara estados por su total.
- **Fuente:** igual que la escena 1.

---

## Escena 3 · De junio a septiembre de 2026 el Tren Maya llevó entre 18 % y 28 % menos pasajeros que en los mismos meses de 2025

- **Subtítulo:** pasajeros transportados por mes en toda la red, enero de 2025 a septiembre de 2026.
- **Archivo:** [`datos/escena-3.csv`](datos/escena-3.csv) · **Gráfica D3:** [`graficas/escena-3.html`](graficas/escena-3.html)
- **Cómo leer esta escena:**
  - La línea gris es 2025 y la morada, 2026, mes contra mes.
  - 2026 empezó arriba: +8.6 % en enero y +11.9 % en febrero. Desde junio quedó abajo.
  - Agosto tuvo la mayor caída (−27.7 %). Septiembre de 2026, con 66,801 pasajeros, es el mes más bajo de la serie.
- **Fuente:** Tren Maya, prestación del servicio ferroviario de pasajeros, datos abiertos en datos.gob.mx. Tabla gold `ind_tren_maya_mensual`.

---

## Escena 4 · En Mérida, 350 de 526 AGEB urbanas ganaron negocios, pero la del Centro perdió 507

- **Subtítulo:** negocios ganados o perdidos en cada AGEB urbana del municipio de Mérida, de noviembre de 2019 a mayo de 2025.
- **Archivos:** [`datos/escena-4.csv`](datos/escena-4.csv) y [`datos/merida_ageb.geojson`](datos/merida_ageb.geojson) · **Gráfica D3:** [`graficas/escena-4.html`](graficas/escena-4.html)
- **Cómo leer esta escena:**
  - El morado marca las AGEB que ganaron negocios y el oro, las que perdieron.
  - El municipio pasó de 52,675 a 55,864 negocios (+6.1 %).
  - La AGEB del Centro (`3105000010510`), la que más negocios tiene, bajó de 3,400 a 2,893 (−14.9 %).
  - Las AGEB de la periferia, a más de 20 km de la estación Teya, crecieron 47.6 %.
  - Las AGEB con marginación alta y muy alta crecieron 40.1 % y 52.3 %, aunque partían de pocos negocios.
  - El mapa encuadra la ciudad. Las 43 AGEB urbanas de las comisarías quedan fuera del recuadro, pero cuentan en los totales.
- **Fuente:** INEGI, DENUE noviembre 2019 y mayo 2025, Censo de Población y Vivienda 2020 y Marco Geoestadístico 2025; CONAPO, índice de marginación urbana 2020. Tabla gold `ind_negocios_ageb_merida`.

---

## Lo que estos datos no dicen

1. **No prueban que el tren causó el cambio.** El DENUE de 2019 es anterior a la obra y el de mayo de 2025 llega año y medio después de la apertura (diciembre de 2023). En medio también hubo pandemia y crecimiento urbano.
2. **El DENUE cuenta establecimientos, no ventas ni empleos.** Si un negocio cierra y otro abre en el mismo lugar, el conteo no cambia.
3. **Los estados no se comparan por su total.** Chiapas solo tiene la estación de Palenque y Tabasco tiene tres, frente a las once de Campeche y las doce de Quintana Roo.
4. **Los pasajeros son de toda la red.** El dato por estación se pidió por transparencia (folio 343053500035426). La respuesta vence el 23 de diciembre de 2026.
5. **La estación Teya está en Kanasín,** a 6.4 km del centro de la AGEB urbana de Mérida más cercana. El mapa de la escena 4 muestra cómo cambió la ciudad, no el efecto directo de la estación.
6. **La población por AGEB es la del Censo 2020.** Las 19 AGEB nuevas del Marco Geoestadístico 2025 no tienen dato del Censo y aparecen en blanco.

---

## Cómo se regenera

```bash
python src/booklet.py
```

El script toma los datos del data mart del DENUE y de la capa gold, y escribe `datos/`, `graficas/datos.js` y las páginas `graficas/escena-N.html`. Los títulos y las lecturas se editan en `index.html`. Las gráficas usan D3 7.9.0.

Para verlas, se abre `index.html` en el navegador; funciona también sin servidor, con la copia de los datos en `graficas/datos.js`. Con servidor:

```bash
python -m http.server -d booklet
```
