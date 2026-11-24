# Power BI — Modelo de Datos

## Tren Maya Data Mart

Este documento describe cómo construir en Power BI el modelo dimensional del proyecto:

**El tren que movió el mapa: ¿qué cambió alrededor de 34 estaciones?**

---

## 1. Tablas que deben importarse

Los archivos se encuentran en:

```text
data/mart/
```

Importar las siguientes seis tablas:

```text
dim_station.parquet
dim_time.parquet
dim_distance.parquet
dim_activity.parquet
dim_employment.parquet
fact_business.parquet
```

---

## 2. Modelo estrella

La tabla central es:

```text
fact_business
```

Las cinco dimensiones deben conectarse directamente con esta tabla.

```text
                    dim_station
                         |
                         |
                         v
dim_time -------> fact_business <------- dim_activity
                         ^
                         |
                  dim_distance
                         ^
                         |
                 dim_employment
```

No crear relaciones entre las dimensiones.

---

## 3. Relaciones

Crear exactamente estas relaciones:

| Dimensión | Clave dimensión | Tabla de hechos | Clave fact | Cardinalidad |
|---|---|---|---|---|
| dim_station | station_key | fact_business | station_key | 1:* |
| dim_time | time_key | fact_business | time_key | 1:* |
| dim_distance | distance_key | fact_business | distance_key | 1:* |
| dim_activity | activity_key | fact_business | activity_key | 1:* |
| dim_employment | employment_key | fact_business | employment_key | 1:* |

Todas las relaciones deben estar:

- Activas
- Cardinalidad **uno a varios (1:*)**
- Dirección de filtro **Single**
- Desde la dimensión hacia `fact_business`

---

## 4. Grano de fact_business

Cada fila de `fact_business` representa una combinación única de:

```text
Estación
+ Año
+ Anillo de distancia
+ Actividad económica
+ Estrato de personal
```

La medida almacenada es:

```text
establishment_count
```

que representa el número de establecimientos DENUE correspondiente a esa combinación.

---

## 5. dim_station

Campos:

```text
station_key
station_id
station_name
state
municipality
latitude
longitude
```

Uso principal:

- Mapas
- Filtros por estación
- Filtros por estado
- Comparaciones entre estaciones
- Análisis territorial

### Geografía

En Power BI configurar:

```text
latitude  → Latitude
longitude → Longitude
```

No agregar ni promediar las coordenadas cuando se utilicen para representar la ubicación de una estación.

---

## 6. dim_time

Campos:

```text
time_key
snapshot_year
```

Valores:

```text
2019
2025
```

`snapshot_year` representa el año del corte DENUE utilizado.

---

## 7. dim_distance

Campos:

```text
distance_key
distance_band
min_km
max_km
```

Anillos:

```text
0-1 km
1-3 km
3-5 km
```

Los anillos son mutuamente excluyentes.

Cada establecimiento fue asignado únicamente a su estación más cercana.

---

## 8. dim_activity

Campos:

```text
activity_key
codigo_act
nombre_act
sector_code
sector_name
```

Permite analizar los establecimientos en dos niveles:

### Actividad detallada

```text
codigo_act
nombre_act
```

### Sector económico

```text
sector_code
sector_name
```

Para el dashboard general se recomienda utilizar `sector_name`.

---

## 9. dim_employment

Campos:

```text
employment_key
employment_range
```

`employment_range` representa el estrato de personal ocupado reportado por DENUE.

IMPORTANTE:

No representa un número exacto de trabajadores.

Por lo tanto, no debe utilizarse para calcular una cifra exacta de empleos generados.

---

## 10. fact_business

Campos:

```text
station_key
time_key
distance_key
activity_key
employment_key
establishment_count
```

### Medida base

La medida principal del modelo debe construirse como:

```DAX
Negocios =
SUM ( fact_business[establishment_count] )
```

No utilizar `COUNTROWS(fact_business)` para calcular establecimientos.

`fact_business` contiene datos agregados, por lo que una fila puede representar múltiples establecimientos.

---

## 11. Resultados de control

Después de crear correctamente las relaciones, la medida:

```DAX
Negocios =
SUM ( fact_business[establishment_count] )
```

debe producir:

| Año | Negocios |
|---|---:|
| 2019 | 39,350 |
| 2025 | 44,838 |
| Total | 84,188 |

Si Power BI no reproduce estos resultados, revisar las relaciones antes de construir el dashboard.

---

## 12. Reglas importantes

### Sí hacer

- Utilizar esquema estrella.
- Utilizar las dimensiones para filtros y ejes.
- Utilizar `establishment_count` para calcular negocios.
- Mantener relaciones 1:*.
- Mantener filtro Single desde dimensión hacia fact.

### No hacer

- No relacionar dimensiones entre sí.
- No crear relaciones muchos-a-muchos.
- No sumar `station_key`, `activity_key`, etc.
- No usar `COUNTROWS(fact_business)` como número de negocios.
- No interpretar `employment_range` como empleos exactos.
- No interpretar el cambio 2019-2025 como causalidad del Tren Maya.

---

## 13. Interpretación metodológica

El modelo permite responder:

> ¿Cómo cambió la actividad empresarial registrada alrededor de las 34 estaciones entre los cortes DENUE 2019 y 2025?

Los resultados representan una comparación descriptiva temporal y espacial.

El modelo **no demuestra causalidad**.

Por lo tanto, en el dashboard y la presentación se recomienda utilizar expresiones como:

- "Cambio observado"
- "Crecimiento registrado"
- "Variación entre 2019 y 2025"
- "Establecimientos alrededor de las estaciones"

Evitar afirmaciones como:

- "Negocios creados por el Tren Maya"
- "Empleos generados por el Tren Maya"
- "Impacto causado por el Tren Maya"
