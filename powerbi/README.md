# Power BI Handoff — Tren Maya Data Mart

## El tren que movió el mapa: ¿qué cambió alrededor de 34 estaciones?

Esta carpeta contiene las instrucciones necesarias para construir y validar el dashboard de Power BI utilizando el Data Mart preparado para el proyecto.

---

## 1. Archivos de esta carpeta

### `data_model.md`

Explica:

- tablas que deben cargarse;
- esquema estrella;
- relaciones;
- cardinalidades;
- dirección de filtros;
- significado de cada dimensión.

### `dax_measures.md`

Contiene las medidas DAX necesarias para:

- Negocios 2019
- Negocios 2025
- Cambio absoluto
- Cambio porcentual
- Participación porcentual

### `expected_results.md`

Contiene resultados previamente validados para comprobar que Power BI está configurado correctamente.

---

# 2. Orden recomendado de trabajo

Seguir este orden:

```text
1. Importar Data Mart
        ↓
2. Crear relaciones
        ↓
3. Crear medidas DAX
        ↓
4. Validar resultados
        ↓
5. Crear visualizaciones
        ↓
6. Aplicar filtros e interacciones
        ↓
7. Diseño visual final
```

No comenzar el diseño del dashboard antes de validar los resultados.

---

# 3. Fuente de datos

Los archivos finales están disponibles en:

```text
data/mart/
```

Importar:

```text
dim_station.parquet
dim_time.parquet
dim_distance.parquet
dim_activity.parquet
dim_employment.parquet
fact_business.parquet
```

También es posible conectar Power BI a PostgreSQL.

---

# 4. Modelo

El modelo debe utilizar esquema estrella:

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

Consultar:

```text
powerbi/data_model.md
```

para las relaciones exactas.

---

# 5. Medidas principales

Crear primero:

```text
Negocios
Negocios 2019
Negocios 2025
Cambio Absoluto
Cambio %
```

Las fórmulas están disponibles en:

```text
powerbi/dax_measures.md
```

Antes de continuar, Power BI debe producir:

```text
Negocios 2019      39,350
Negocios 2025      44,838
Cambio              5,488
Cambio %            13.95%
```

---

# 6. Diseño propuesto

Se recomienda construir cuatro páginas.

---

# Página 1 — Panorama General

## Objetivo

Responder rápidamente:

> ¿Cómo cambió la actividad empresarial alrededor de las estaciones entre 2019 y 2025?

## Encabezado

Título:

```text
El tren que movió el mapa
```

Subtítulo:

```text
Cambio en la actividad empresarial alrededor de 34 estaciones
DENUE 2019-2025
```

## Tarjetas KPI

Mostrar:

```text
Negocios 2019
39,350
```

```text
Negocios 2025
44,838
```

```text
Cambio absoluto
+5,488
```

```text
Cambio
+13.95%
```

## Visual 1 — Mapa

Utilizar:

```text
Latitude:
dim_station[latitude]

Longitude:
dim_station[longitude]

Location/Tooltip:
dim_station[station_name]
```

Tamaño recomendado:

```text
[Negocios 2025]
```

Tooltips:

```text
Estado
Municipio
Negocios 2019
Negocios 2025
Cambio Absoluto
Cambio %
```

## Visual 2 — Comparación por distancia

Gráfico de columnas agrupadas.

Eje:

```text
dim_distance[distance_band]
```

Valores:

```text
[Negocios 2019]
[Negocios 2025]
```

## Visual 3 — Cambio por estación

Gráfico de barras.

Eje:

```text
dim_station[station_name]
```

Valor:

```text
[Cambio Absoluto]
```

Ordenar de mayor a menor.

## Filtros

Agregar slicers:

```text
Estado
Estación
Sector
Distancia
```

---

# Página 2 — Estaciones

## Objetivo

Analizar cuáles estaciones presentan los principales cambios entre ambos cortes.

## Visual 1 — Ranking

Gráfico de barras horizontal.

Categoría:

```text
dim_station[station_name]
```

Valor:

```text
[Cambio Absoluto]
```

Orden:

```text
Mayor → menor
```

## Visual 2 — Comparación 2019 vs 2025

Columnas agrupadas.

Eje:

```text
dim_station[station_name]
```

Valores:

```text
[Negocios 2019]
[Negocios 2025]
```

## Visual 3 — Tabla detallada

Columnas:

```text
Estado
Estación
Negocios 2019
Negocios 2025
Cambio Absoluto
Cambio %
```

Aplicar formato condicional al cambio.

## Resultados de referencia

Entre los controles conocidos:

```text
Tulum
1,675 → 2,575
+900
+53.73%
```

```text
Palenque
4,643 → 5,375
+732
+15.77%
```

```text
Mérida Teya
1,392 → 2,069
+677
+48.64%
```

```text
Chetumal Aeropuerto
5,117 → 4,927
-190
-3.71%
```

---

# Página 3 — Sectores Económicos

## Objetivo

Identificar qué actividades económicas explican los principales cambios observados.

## Visual 1 — Cambio por sector

Gráfico de barras.

Eje:

```text
dim_activity[sector_name]
```

Valor:

```text
[Cambio Absoluto]
```

Ordenar de mayor a menor.

## Visual 2 — Comparación temporal

Columnas agrupadas.

Eje:

```text
dim_activity[sector_name]
```

Valores:

```text
[Negocios 2019]
[Negocios 2025]
```

## Visual 3 — Tabla sectorial

Mostrar:

```text
sector_code
sector_name
Negocios 2019
Negocios 2025
Cambio Absoluto
Cambio %
```

## Control importante

Comercio al por menor:

```text
2019: 14,730
2025: 18,081
Cambio: +3,351
Cambio %: +22.75%
```

---

# Página 4 — Distancia y estructura empresarial

## Objetivo

Analizar cómo varió la actividad empresarial según la distancia respecto de las estaciones.

## Visual 1 — Anillos de distancia

Columnas agrupadas.

Eje:

```text
dim_distance[distance_band]
```

Valores:

```text
[Negocios 2019]
[Negocios 2025]
```

Resultados esperados:

```text
0-1 km
3,823 → 4,307
+12.66%

1-3 km
16,396 → 19,047
+16.17%

3-5 km
19,131 → 21,484
+12.30%
```

## Visual 2 — Cambio porcentual

Barras.

Eje:

```text
dim_distance[distance_band]
```

Valor:

```text
[Cambio %]
```

## Visual 3 — Estrato de personal

Eje:

```text
dim_employment[employment_range]
```

Valores:

```text
[Negocios 2019]
[Negocios 2025]
```

Esto permite estudiar la composición de los establecimientos según el estrato de personal ocupado.

No interpretar estos rangos como cantidades exactas de empleos.

---

# 7. Filtros globales recomendados

Siempre que el diseño lo permita:

```text
Estado
Estación
Sector económico
Anillo de distancia
Estrato de personal
```

Evitar agregar filtros que no aporten información a la pregunta de investigación.

---

# 8. Interacciones

Comprobar que:

- seleccionar un estado filtre sus estaciones;
- seleccionar una estación actualice KPIs y gráficos;
- seleccionar un sector actualice las comparaciones;
- seleccionar un anillo actualice el resto de visualizaciones;
- las tarjetas respondan correctamente a los filtros.

---

# 9. Storytelling

El dashboard debe contar una historia, no solamente mostrar gráficas.

Secuencia sugerida:

```text
¿Cuánto cambió?
        ↓
¿Dónde cambió?
        ↓
¿En qué sectores?
        ↓
¿A qué distancia?
        ↓
¿Qué podemos concluir?
```

Hallazgo general:

```text
39,350 → 44,838
+5,488 establecimientos
+13.95%
```

Hallazgos que pueden destacarse:

```text
Tulum:
+900 establecimientos
+53.73%
```

```text
Mérida Teya:
+677
+48.64%
```

```text
Anillo 1-3 km:
+16.17%
```

```text
Comercio al por menor:
+3,351
+22.75%
```

---

# 10. Interpretación

El dashboard compara establecimientos registrados por DENUE alrededor de las estaciones entre 2019 y 2025.

Debe utilizarse lenguaje como:

```text
"Cambio observado"
"Crecimiento registrado"
"Variación entre los cortes DENUE"
```

No afirmar:

```text
"El Tren Maya creó 5,488 negocios."
```

El análisis es descriptivo y no demuestra causalidad.

Otros factores pueden contribuir a los cambios observados, incluyendo crecimiento urbano, turismo, inversión, recuperación posterior a la pandemia y tendencias económicas regionales.

---

# 11. Checklist final

Antes de considerar terminado Power BI:

- [ ] Las seis tablas están cargadas.
- [ ] Las cinco relaciones son 1:*.
- [ ] Las relaciones están activas.
- [ ] La dirección de filtro es dimensión → fact.
- [ ] Negocios 2019 = 39,350.
- [ ] Negocios 2025 = 44,838.
- [ ] Cambio = +5,488.
- [ ] Cambio % = +13.95%.
- [ ] Tulum = 1,675 → 2,575.
- [ ] 1-3 km = 16,396 → 19,047.
- [ ] Comercio al por menor = 14,730 → 18,081.
- [ ] El mapa contiene las 34 estaciones.
- [ ] Los slicers funcionan correctamente.
- [ ] Las visualizaciones responden a los filtros.
- [ ] Los porcentajes están formateados correctamente.
- [ ] No se hacen afirmaciones causales.
- [ ] El dashboard tiene títulos y unidades claras.

---

# 12. Documentación relacionada

Modelo:

```text
powerbi/data_model.md
```

DAX:

```text
powerbi/dax_measures.md
```

Resultados de validación:

```text
powerbi/expected_results.md
```

Data Mart:

```text
data/mart/
```

Validación automática del backend:

```bash
python src/validate_datamart.py
```
