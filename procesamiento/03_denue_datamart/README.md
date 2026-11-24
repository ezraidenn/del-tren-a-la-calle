# Tren Maya Data Mart

## El tren que movió el mapa: ¿qué cambió alrededor de 34 estaciones?

Proyecto de **Business Intelligence y Data Engineering** para analizar cómo cambió la actividad empresarial alrededor de 34 estaciones del Tren Maya entre 2019 y 2025, utilizando información del **Directorio Estadístico Nacional de Unidades Económicas (DENUE)** de INEGI.

> **Pregunta de investigación:**  
> ¿Cómo cambió la actividad empresarial alrededor de las 34 estaciones del Tren Maya entre 2019 y 2025?

---

## Objetivo

Construir un Data Mart reproducible que permita comparar la actividad empresarial registrada alrededor de las estaciones del Tren Maya utilizando dos cortes temporales:

- DENUE noviembre de 2019
- DENUE mayo de 2025

El backend procesa más de **1.1 millones de registros originales**, realiza análisis geoespacial y genera un esquema estrella preparado para PostgreSQL y herramientas de Business Intelligence como Power BI.

---

## Arquitectura

```text
DENUE 2019 + DENUE 2025
          |
          v
   Validación RAW
          |
          v
     Normalización
          |
          v
Procesamiento geoespacial
          |
          v
 Estación más cercana
          |
          v
Anillos: 0-1 / 1-3 / 3-5 km
          |
          v
     Data Mart
    (Star Schema)
          |
          v
     PostgreSQL
          |
          v
   Vistas analíticas
          |
          v
      Power BI
```

---

## Alcance de los datos

El análisis utiliza información DENUE de cinco estados:

- Chiapas
- Tabasco
- Campeche
- Yucatán
- Quintana Roo

Registros originales procesados:

| Corte DENUE | Registros |
|---|---:|
| 2019 | 533,275 |
| 2025 | 604,594 |
| **Total** | **1,137,869** |

El catálogo geográfico contiene **34 estaciones del Tren Maya**.

---

## Metodología geoespacial

Cada establecimiento DENUE se asigna a su **estación más cercana** utilizando sus coordenadas geográficas.

La distancia se calcula mediante **Haversine** utilizando `BallTree` de Scikit-learn.

Solo se conservan establecimientos localizados a un máximo de **5 km** de alguna estación.

Los anillos son mutuamente excluyentes:

| Anillo | Interpretación |
|---|---|
| 0-1 km | Entorno inmediato |
| 1-3 km | Entorno cercano |
| 3-5 km | Área de influencia ampliada |

Si un establecimiento está a menos de 5 km de varias estaciones, se asigna únicamente a la **estación más cercana**, evitando doble conteo.

---

## Pipeline de datos

Los scripts del pipeline se encuentran en `src/`.

Los ZIP originales del DENUE (10 archivos: 5 estados por 2 ediciones) están en la carpeta común del repositorio, `datos/originales/03_inegi/3.1_denue_2019_11/` y `datos/originales/03_inegi/3.2_denue_2025_05/`, con su URL, fecha y SHA-256 en `procedencia.json`. Para volver a bajarlos: `python src/03_inegi.py` desde la raíz del repositorio.

Orden de ejecución, desde esta carpeta:

```bash
python src/validate_raw.py
python src/prepare_denue.py
python src/geospatial_match.py
python src/analyze_station_change.py
python src/build_datamart.py
python src/validate_datamart.py
```

Con los ZIP del repositorio, el pipeline reproduce el Data Mart incluido sin diferencias en ninguna de sus 6 tablas.

### `validate_raw.py`

Valida los archivos DENUE originales:

- estructura de los ZIP;
- columnas requeridas;
- número de registros;
- coordenadas geográficas.

### `prepare_denue.py`

Normaliza los cortes DENUE 2019 y 2025 a una estructura común y genera archivos Parquet intermedios.

### `geospatial_match.py`

Calcula la estación más cercana a cada establecimiento y su distancia mediante BallTree + Haversine.

También clasifica cada establecimiento en los anillos de distancia definidos.

### `analyze_station_change.py`

Genera comparaciones de establecimientos entre 2019 y 2025 por estación y anillo de distancia.

### `build_datamart.py`

Construye las dimensiones y la tabla de hechos del esquema estrella.

### `load_postgres.py`

Carga el Data Mart final en PostgreSQL y ejecuta validaciones de integridad y totales.

---

## Modelo dimensional

El Data Mart utiliza un **esquema estrella**.

```text
                    dim_station
                         |
                         |
dim_time -------- fact_business -------- dim_activity
                         |
                         |
                  dim_distance
                         |
                         |
                 dim_employment
```

### Tabla de hechos

`fact_business`

**Grano:**

> Estación + año + anillo de distancia + actividad SCIAN + estrato de personal.

**Medida principal:**

`establishment_count`

### Dimensiones

| Tabla | Descripción |
|---|---|
| `dim_station` | 34 estaciones, ubicación y coordenadas |
| `dim_time` | Cortes 2019 y 2025 |
| `dim_distance` | Anillos 0-1, 1-3 y 3-5 km |
| `dim_activity` | Actividades económicas y sectores SCIAN |
| `dim_employment` | Estrato de personal ocupado |

La tabla `fact_business` contiene **18,061 combinaciones agregadas** que representan **84,188 registros de establecimientos** dentro de los 5 km analizados en ambos cortes.

---

## Data Mart incluido

Para facilitar el trabajo del equipo, las tablas finales se incluyen directamente en:

```text
data/mart/
```

Contenido:

```text
dim_activity.parquet
dim_distance.parquet
dim_employment.parquet
dim_station.parquet
dim_time.parquet
fact_business.parquet
```

Estos archivos ocupan aproximadamente **104 KB**, por lo que es posible trabajar con el Data Mart sin volver a procesar los archivos DENUE originales.

Los datos RAW e intermedios no se almacenan en GitHub debido a su tamaño.

---

## Resultados principales

### Cambio global

Establecimientos localizados hasta 5 km de las estaciones:

| Año | Establecimientos |
|---|---:|
| 2019 | 39,350 |
| 2025 | 44,838 |

**Cambio absoluto:** +5,488 establecimientos  
**Variación:** +13.95%

### Cambio por distancia

| Distancia | 2019 | 2025 | Cambio | Variación |
|---|---:|---:|---:|---:|
| 0-1 km | 3,823 | 4,307 | +484 | +12.66% |
| 1-3 km | 16,396 | 19,047 | +2,651 | +16.17% |
| 3-5 km | 19,131 | 21,484 | +2,353 | +12.30% |

### Estaciones con mayor incremento absoluto observado

| Estación | 2019 | 2025 | Cambio | Variación |
|---|---:|---:|---:|---:|
| Tulum | 1,675 | 2,575 | +900 | +53.73% |
| Palenque | 4,643 | 5,375 | +732 | +15.77% |
| Mérida Teya | 1,392 | 2,069 | +677 | +48.64% |
| San Francisco de Campeche | 4,853 | 5,468 | +615 | +12.67% |
| Escárcega | 2,345 | 2,684 | +339 | +14.46% |

### Sectores con mayor incremento absoluto observado

| Sector | 2019 | 2025 | Cambio | Variación |
|---|---:|---:|---:|---:|
| Comercio al por menor | 14,730 | 18,081 | +3,351 | +22.75% |
| Otros servicios excepto actividades gubernamentales | 6,045 | 6,979 | +934 | +15.45% |
| Alojamiento temporal y preparación de alimentos y bebidas | 6,020 | 6,808 | +788 | +13.09% |

---

## PostgreSQL

El esquema relacional se encuentra en:

```text
sql/create_schema.sql
```

Las consultas analíticas están en:

```text
sql/analysis_queries.sql
```

Y las vistas preparadas para análisis se encuentran en:

```text
sql/create_views.sql
```

### Vistas disponibles

| Vista | Uso |
|---|---|
| `vw_business_analysis` | Dataset analítico detallado |
| `vw_station_change` | Comparación 2019 vs. 2025 por estación |
| `vw_sector_change` | Comparación por sector económico |
| `vw_distance_change` | Comparación por anillo de distancia |

---

## Uso con Power BI

El equipo de visualización puede consumir el proyecto de tres formas:

1. Conectando Power BI directamente a PostgreSQL.
2. Utilizando las vistas SQL preparadas.
3. Importando los archivos Parquet de `data/mart/`.

Para un modelo dimensional completo se recomienda utilizar las tablas del esquema estrella.

### KPIs sugeridos

- Establecimientos 2019
- Establecimientos 2025
- Cambio absoluto
- Cambio porcentual
- Cambio por estación
- Cambio por estado
- Cambio por anillo de distancia
- Cambio por sector SCIAN
- Distribución por estrato de personal

### Visualizaciones sugeridas

- Mapa de las 34 estaciones
- Comparación 2019 vs. 2025
- Ranking por cambio absoluto
- Variación porcentual por estación
- Cambio por sector económico
- Comparación por anillo de distancia
- Filtros por estado, estación, sector y distancia

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/ezraidenn/del-tren-a-la-calle.git
cd del-tren-a-la-calle/procesamiento/03_denue_datamart
```

### 2. Instalar dependencias

Se recomienda utilizar un entorno virtual.

```bash
pip install -r requirements.txt
```

### 3. Crear el esquema PostgreSQL

```bash
psql -U <usuario> -d <base_de_datos> -f sql/create_schema.sql
```

### 4. Cargar el Data Mart

```bash
python src/load_postgres.py
```

### 5. Crear las vistas analíticas

```bash
psql -U <usuario> -d <base_de_datos> -f sql/create_views.sql
```

Las credenciales de PostgreSQL no se almacenan en el repositorio.

---

## Estructura del repositorio

```text
03_denue_datamart/
│
├── data/
│   ├── mart/
│   │   ├── dim_activity.parquet
│   │   ├── dim_distance.parquet
│   │   ├── dim_employment.parquet
│   │   ├── dim_station.parquet
│   │   ├── dim_time.parquet
│   │   └── fact_business.parquet
│   │
│   └── reference/
│       └── estaciones_tren_maya_catalogo_maestro.csv
│
├── sql/
│   ├── analysis_queries.sql
│   ├── create_schema.sql
│   └── create_views.sql
│
├── src/
│   ├── analyze_station_change.py
│   ├── build_datamart.py
│   ├── geospatial_match.py
│   ├── load_postgres.py
│   ├── prepare_denue.py
│   └── validate_raw.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Tecnologías utilizadas

- Python 3
- Pandas
- NumPy
- PyArrow
- Scikit-learn
- PostgreSQL
- SQL
- DENUE / INEGI
- Power BI

---

## Consideraciones metodológicas

Este proyecto realiza un análisis **descriptivo, temporal y espacial**.

Los resultados muestran cómo cambió el número de establecimientos registrados en DENUE alrededor de las estaciones entre 2019 y 2025.

**No se interpreta esta diferencia como un efecto causal del Tren Maya.**

Los cambios observados pueden estar relacionados también con:

- crecimiento urbano;
- recuperación posterior a la pandemia;
- turismo;
- inversión pública y privada;
- cambios demográficos;
- tendencias económicas regionales;
- cambios en el propio directorio DENUE.

Por ello, expresiones como *“crecimiento observado alrededor de las estaciones”* son metodológicamente más apropiadas que afirmar que el Tren Maya *“creó”* determinada cantidad de negocios.

---

## Fuente principal

**INEGI — Directorio Estadístico Nacional de Unidades Económicas (DENUE)**

Cortes utilizados:

- Noviembre 2019
- Mayo 2025

---

## Estado del proyecto

**Backend / Data Engineering:** completado  
**Data Mart:** completado  
**PostgreSQL:** completado  
**Vistas analíticas:** completadas  
**Dashboard Power BI:** en desarrollo
