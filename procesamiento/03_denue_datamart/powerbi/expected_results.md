# Power BI — Resultados Esperados

## Tren Maya Data Mart

Este documento contiene los resultados de control obtenidos y validados en el backend.

Su objetivo es comprobar que el modelo de Power BI reproduce correctamente los resultados del Data Mart.

---

## 1. Validación general

El Data Mart contiene:

| Elemento | Resultado |
|---|---:|
| Estaciones | 34 |
| Años | 2 |
| Anillos de distancia | 3 |
| Actividades económicas | 717 |
| Estratos de personal | 7 |
| Filas de fact_business | 18,061 |

La suma de `establishment_count` debe ser:

```text
84,188
```

---

## 2. Totales por año

| Año | Establecimientos |
|---|---:|
| 2019 | 39,350 |
| 2025 | 44,838 |
| Total | 84,188 |

Cambio absoluto:

```text
+5,488
```

Cambio porcentual:

```text
+13.95%
```

Fórmula:

```text
(44,838 - 39,350) / 39,350 × 100
```

---

## 3. Resultados por distancia

| Distancia | 2019 | 2025 | Cambio | Cambio % |
|---|---:|---:|---:|---:|
| 0-1 km | 3,823 | 4,307 | +484 | +12.66% |
| 1-3 km | 16,396 | 19,047 | +2,651 | +16.17% |
| 3-5 km | 19,131 | 21,484 | +2,353 | +12.30% |

Control:

```text
2019:
3,823 + 16,396 + 19,131 = 39,350

2025:
4,307 + 19,047 + 21,484 = 44,838
```

El anillo con mayor crecimiento porcentual observado es:

```text
1-3 km → +16.17%
```

---

## 4. Resultados de control por estación

Algunos valores que pueden utilizarse para verificar filtros y visualizaciones:

| Estación | 2019 | 2025 | Cambio | Cambio % |
|---|---:|---:|---:|---:|
| Tulum | 1,675 | 2,575 | +900 | +53.73% |
| Palenque | 4,643 | 5,375 | +732 | +15.77% |
| Mérida Teya | 1,392 | 2,069 | +677 | +48.64% |
| San Francisco de Campeche | 4,853 | 5,468 | +615 | +12.67% |
| Candelaria | 1,060 | 1,017 | -43 | -4.06% |
| Chetumal Aeropuerto | 5,117 | 4,927 | -190 | -3.71% |

También existen estaciones sin establecimientos dentro del radio analizado en ambos cortes:

```text
Edzná
Calakmul
```

En esos casos:

```text
2019 = 0
2025 = 0
```

---

## 5. Resultados por sector SCIAN

Los siguientes sectores sirven como controles adicionales.

### Comercio al por menor

Código:

```text
46
```

Resultados:

```text
2019: 14,730
2025: 18,081
Cambio: +3,351
Cambio %: +22.75%
```

### Otros servicios excepto actividades gubernamentales

Código:

```text
81
```

Resultados:

```text
2019: 6,045
2025: 6,979
Cambio: +934
Cambio %: +15.45%
```

### Servicios de alojamiento temporal y de preparación de alimentos y bebidas

Código:

```text
72
```

Resultados:

```text
2019: 6,020
2025: 6,808
Cambio: +788
Cambio %: +13.09%
```

---

## 6. Prueba de las medidas DAX

Sin ningún filtro activo:

```text
[Negocios]          = 84,188
[Negocios 2019]     = 39,350
[Negocios 2025]     = 44,838
[Cambio Absoluto]   = 5,488
[Cambio %]          = 13.95%
```

Si estos valores coinciden, la agregación principal funciona correctamente.

---

## 7. Prueba de filtros

### Filtro Tulum

Al seleccionar únicamente:

```text
station_name = Tulum
```

Power BI debe mostrar:

```text
Negocios 2019:   1,675
Negocios 2025:   2,575
Cambio:            900
Cambio %:        53.73%
```

### Filtro 1-3 km

Al seleccionar:

```text
distance_band = 1-3 km
```

debe mostrar:

```text
Negocios 2019: 16,396
Negocios 2025: 19,047
Cambio:         2,651
Cambio %:       16.17%
```

### Filtro sector 46

Al seleccionar Comercio al por menor:

```text
Negocios 2019: 14,730
Negocios 2025: 18,081
Cambio:         3,351
Cambio %:       22.75%
```

---

## 8. Casos especiales

Existen estaciones donde 2019 puede ser cero y 2025 mayor que cero.

En estos casos:

```text
Cambio % = BLANK()
```

es un resultado correcto.

No debe sustituirse automáticamente por:

```text
100%
```

porque no existe una base distinta de cero sobre la cual calcular el crecimiento porcentual.

---

## 9. Checklist antes de diseñar el dashboard

Antes de trabajar en colores, mapas o diseño visual, comprobar:

- [ ] 34 estaciones cargadas.
- [ ] 717 actividades cargadas.
- [ ] 3 anillos de distancia.
- [ ] 18,061 filas en fact_business.
- [ ] 39,350 establecimientos en 2019.
- [ ] 44,838 establecimientos en 2025.
- [ ] 84,188 en ambos cortes.
- [ ] Cambio absoluto de +5,488.
- [ ] Cambio porcentual de +13.95%.
- [ ] Tulum reproduce 1,675 → 2,575.
- [ ] El anillo 1-3 km reproduce 16,396 → 19,047.
- [ ] Comercio al por menor reproduce 14,730 → 18,081.

Si alguno de estos controles falla, revisar el modelo antes de continuar con el dashboard.

---

## 10. Nota metodológica

Estos resultados describen cambios en los establecimientos registrados por DENUE alrededor de las estaciones entre 2019 y 2025.

No constituyen una estimación causal del efecto del Tren Maya.

Por ello, en Power BI y en la presentación utilizar:

```text
"Cambio observado entre 2019 y 2025"
```

en lugar de:

```text
"Negocios creados por el Tren Maya"
```
