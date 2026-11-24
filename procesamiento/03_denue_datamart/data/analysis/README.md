# Analytical Outputs — Tren Maya Data Mart

Esta carpeta contiene resultados analíticos derivados del Data Mart del proyecto **“El tren que movió el mapa: qué cambió alrededor de 34 estaciones”**.

El análisis compara establecimientos DENUE de 2019 y 2025 ubicados dentro de un radio máximo de 5 km alrededor de las estaciones estudiadas.

## 1. Resultado global

| Año | Establecimientos |
|---|---:|
| 2019 | 39,350 |
| 2025 | 44,838 |

Cambio observado:

- Cambio absoluto: **+5,488**
- Cambio porcentual: **+13.95%**

Todos los análisis derivados deben reconciliar con estos valores.

## 2. Archivos

### `state_change.csv`

Generado por:

```bash
python src/analyze_state_change.py
```

Contiene el cambio agregado por estado.

| Estado | 2019 | 2025 | Cambio | Cambio % |
|---|---:|---:|---:|---:|
| Campeche | 11,851 | 13,397 | +1,546 | +13.05% |
| Quintana Roo | 12,126 | 13,604 | +1,478 | +12.19% |
| Yucatán | 7,703 | 8,996 | +1,293 | +16.79% |
| Chiapas | 4,643 | 5,375 | +732 | +15.77% |
| Tabasco | 3,027 | 3,466 | +439 | +14.50% |

**Hallazgo:** Campeche presenta el mayor incremento absoluto observado (+1,546), mientras que Yucatán presenta el mayor crecimiento porcentual (+16.79%).

### `station_sector_change.csv`

Generado por:

```bash
python src/analyze_station_sector.py
```

Desagrega los resultados por:

```text
estación × sector económico × año
```

Permite identificar qué sectores contribuyen al cambio neto observado alrededor de cada estación.

Ejemplos:

**Tulum**
- Comercio al por menor: 558 → 974 (**+416**)
- Alojamiento y preparación de alimentos: 418 → 653 (**+235**)
- Otros servicios excepto actividades gubernamentales: 232 → 355 (**+123**)

**Mérida Teya**
- Comercio al por menor: 613 → 929 (**+316**)
- Alojamiento y preparación de alimentos: 274 → 420 (**+146**)
- Otros servicios excepto actividades gubernamentales: 187 → 310 (**+123**)

**Palenque**
- Comercio al por menor: 1,831 → 2,358 (**+527**)
- Otros servicios excepto actividades gubernamentales: 727 → 853 (**+126**)

También existen contracciones. Por ejemplo:

**Chetumal Aeropuerto — alojamiento y preparación de alimentos**

```text
752 → 650
Cambio: -102
```

### `station_distance_change.csv`

Generado por:

```bash
python src/analyze_station_distance.py
```

Desagrega los resultados por:

```text
estación × anillo de distancia × año
```

Los anillos son mutuamente excluyentes:

- 0–1 km
- 1–3 km
- 3–5 km

Ejemplos:

**Tulum — 3–5 km**

```text
1,488 → 2,200
+712
+47.85%
```

**Mérida Teya — 3–5 km**

```text
1,353 → 1,893
+540
+39.91%
```

**Palenque — 1–3 km**

```text
3,786 → 4,378
+592
+15.64%
```

**Chetumal Aeropuerto — 3–5 km**

```text
3,797 → 3,583
-214
-5.64%
```

## 3. Hallazgos principales

### Crecimiento global

Los establecimientos registrados dentro de los radios analizados aumentaron de **39,350 a 44,838**, equivalente a **+5,488 (+13.95%)**.

### Comercio al por menor

El sector 46, Comercio al por menor, presenta:

```text
2019: 14,730
2025: 18,081
Cambio: +3,351
Cambio %: +22.75%
```

Este sector también aparece entre las principales contribuciones positivas en varias estaciones.

### El patrón espacial no es uniforme

El crecimiento no se concentra en el mismo anillo en todas las estaciones.

Por ejemplo:

```text
Tulum          → principal aumento en 3–5 km
Mérida Teya    → principal aumento en 3–5 km
Palenque       → principal aumento en 1–3 km
```

Por lo tanto, el resultado global por distancia no debe interpretarse como representativo de todas las estaciones.

### También existen contracciones

Ejemplos:

```text
Chetumal Aeropuerto × 3–5 km: -214
Candelaria × 0–1 km:          -76
Chetumal × alojamiento:       -102
```

Los resultados muestran heterogeneidad espacial y sectorial.

## 4. Interpretación de porcentajes

Los cambios porcentuales deben analizarse junto con el volumen absoluto.

Por ejemplo:

```text
Cancún Aeropuerto × 0–1 km

2019: 1
2025: 0

Cambio absoluto: -1
Cambio porcentual: -100%
```

Aunque el porcentaje parece extremo, representa solamente un establecimiento.

Por ello, no deben destacarse porcentajes elevados sin considerar el tamaño de la base.

## 5. Reproducibilidad

Los resultados pueden regenerarse ejecutando:

```bash
python src/analyze_state_change.py
python src/analyze_station_sector.py
python src/analyze_station_distance.py
```

Cada script valida que sus resultados agregados sean:

```text
2019 = 39,350
2025 = 44,838
Cambio = +5,488
```

## 6. Uso en Power BI

Los CSV de esta carpeta sirven como:

- resultados de control;
- apoyo para storytelling;
- validación de visualizaciones;
- análisis complementario;
- referencia para la presentación.

El dashboard principal debe utilizar el esquema estrella ubicado en:

```text
data/mart/
```

Estos CSV son productos analíticos derivados y **no reemplazan al Data Mart**.

## 7. Nota metodológica

Los resultados describen diferencias entre los cortes DENUE 2019 y 2025 dentro de las áreas definidas alrededor de las estaciones.

**No demuestran causalidad.**

Los cambios también pueden estar relacionados con factores como crecimiento urbano, turismo, inversión, recuperación posterior a la pandemia y tendencias económicas regionales.

Se recomienda utilizar expresiones como:

- “cambio observado”;
- “variación registrada”;
- “diferencia entre 2019 y 2025”.

Debe evitarse afirmar:

> “El Tren Maya creó 5,488 negocios.”
