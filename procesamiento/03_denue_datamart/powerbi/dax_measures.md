# Power BI — Medidas DAX

## Tren Maya Data Mart

Estas medidas están diseñadas para el esquema estrella del proyecto.

La tabla de hechos es:

```text
fact_business
```

La medida almacenada es:

```text
establishment_count
```

---

## 1. Medida base

```DAX
Negocios =
SUM ( fact_business[establishment_count] )
```

Resultado esperado sin filtros:

```text
84,188
```

---

## 2. Negocios 2019

```DAX
Negocios 2019 =
CALCULATE (
    [Negocios],
    dim_time[snapshot_year] = 2019
)
```

Resultado global esperado:

```text
39,350
```

---

## 3. Negocios 2025

```DAX
Negocios 2025 =
CALCULATE (
    [Negocios],
    dim_time[snapshot_year] = 2025
)
```

Resultado global esperado:

```text
44,838
```

---

## 4. Cambio absoluto

```DAX
Cambio Absoluto =
[Negocios 2025] - [Negocios 2019]
```

Resultado global esperado:

```text
+5,488
```

---

## 5. Cambio porcentual

```DAX
Cambio % =
DIVIDE (
    [Cambio Absoluto],
    [Negocios 2019]
)
```

Configurar esta medida en Power BI como:

```text
Percentage
2 decimal places
```

Resultado global esperado:

```text
13.95%
```

---

## 6. Participación sobre el total

```DAX
Participacion % =
DIVIDE (
    [Negocios],
    CALCULATE (
        [Negocios],
        REMOVEFILTERS ( dim_station ),
        REMOVEFILTERS ( dim_activity ),
        REMOVEFILTERS ( dim_distance ),
        REMOVEFILTERS ( dim_employment )
    )
)
```

Esta medida puede utilizarse para analizar qué proporción representa una estación, sector o categoría dentro del contexto temporal seleccionado.

---

# Medidas recomendadas para tarjetas KPI

Las tarjetas principales del dashboard deben utilizar:

```text
[Negocios 2019]
[Negocios 2025]
[Cambio Absoluto]
[Cambio %]
```

Valores globales esperados:

| KPI | Resultado |
|---|---:|
| Negocios 2019 | 39,350 |
| Negocios 2025 | 44,838 |
| Cambio Absoluto | +5,488 |
| Cambio % | +13.95% |

---

# Uso por estación

Para comparar estaciones no es necesario crear una medida diferente.

Utilizar:

```text
Eje / categoría:
dim_station[station_name]
```

y como valores:

```text
[Negocios 2019]
[Negocios 2025]
[Cambio Absoluto]
[Cambio %]
```

Ejemplos de control:

| Estación | 2019 | 2025 | Cambio | Cambio % |
|---|---:|---:|---:|---:|
| Tulum | 1,675 | 2,575 | +900 | +53.73% |
| Palenque | 4,643 | 5,375 | +732 | +15.77% |
| Mérida Teya | 1,392 | 2,069 | +677 | +48.64% |
| San Francisco de Campeche | 4,853 | 5,468 | +615 | +12.67% |

Estos valores sirven para validar que el contexto de filtro funciona correctamente.

---

# Uso por distancia

Utilizar:

```text
Eje:
dim_distance[distance_band]
```

Valores:

```text
[Negocios 2019]
[Negocios 2025]
[Cambio Absoluto]
[Cambio %]
```

Resultados esperados:

| Distancia | 2019 | 2025 | Cambio | Cambio % |
|---|---:|---:|---:|---:|
| 0-1 km | 3,823 | 4,307 | +484 | +12.66% |
| 1-3 km | 16,396 | 19,047 | +2,651 | +16.17% |
| 3-5 km | 19,131 | 21,484 | +2,353 | +12.30% |

---

# Uso por sector económico

Utilizar:

```text
Eje:
dim_activity[sector_name]
```

Valores recomendados:

```text
[Negocios 2019]
[Negocios 2025]
[Cambio Absoluto]
[Cambio %]
```

Esto permite identificar qué sectores presentan mayor crecimiento o disminución alrededor de las estaciones.

---

# Mapa

Para el mapa utilizar campos de:

```text
dim_station
```

Ubicación:

```text
latitude
longitude
station_name
```

Como tamaño o valor se puede utilizar:

```text
[Negocios 2025]
```

o:

```text
[Cambio Absoluto]
```

Como tooltip se recomienda incluir:

```text
station_name
state
municipality
[Negocios 2019]
[Negocios 2025]
[Cambio Absoluto]
[Cambio %]
```

---

# Filtros recomendados

Crear slicers utilizando:

```text
dim_station[state]
dim_station[station_name]
dim_distance[distance_band]
dim_activity[sector_name]
dim_employment[employment_range]
```

Para seleccionar el corte temporal directamente también puede utilizarse:

```text
dim_time[snapshot_year]
```

Sin embargo, las medidas `[Negocios 2019]` y `[Negocios 2025]` ya fijan explícitamente sus respectivos años.

---

# Formato recomendado

## Negocios

Formato:

```text
Whole number
Thousands separator: On
```

Ejemplo:

```text
44,838
```

## Cambio Absoluto

Formato:

```text
Whole number
Thousands separator: On
```

## Cambio %

Formato:

```text
Percentage
Decimal places: 2
```

Ejemplo:

```text
13.95%
```

---

# Nota importante sobre valores cero

Algunas estaciones pueden no presentar establecimientos para determinados años o combinaciones de filtros.

En análisis porcentuales, un valor base de 2019 igual a cero no debe interpretarse como crecimiento porcentual infinito.

La función:

```DAX
DIVIDE (
    [Cambio Absoluto],
    [Negocios 2019]
)
```

devuelve `BLANK()` cuando el denominador es cero, evitando porcentajes engañosos.

---

# Reglas de uso

1. Utilizar `[Negocios]`, no `COUNTROWS(fact_business)`.

2. Utilizar campos de las dimensiones para filtros, categorías y ejes.

3. No sumar las columnas `*_key`.

4. Mantener las relaciones del modelo en dirección dimensión → fact.

5. No interpretar `[Cambio Absoluto]` como negocios creados por el Tren Maya.

6. No interpretar `employment_range` como número exacto de trabajadores.

7. Validar los KPIs globales antes de construir las visualizaciones finales.

---

# Validación mínima antes del dashboard

El modelo de Power BI está correctamente configurado si reproduce:

```text
2019              39,350
2025              44,838
Cambio             5,488
Cambio %           13.95%
Total ambos años  84,188
```

Si estos valores no coinciden, revisar primero las relaciones y los tipos de datos antes de modificar las medidas DAX.
