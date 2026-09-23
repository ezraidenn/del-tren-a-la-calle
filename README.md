# Tren Maya Data Mart

## El tren que movió el mapa: ¿qué cambió alrededor de 34 estaciones?

Proyecto de Business Intelligence orientado al análisis de los cambios en la actividad empresarial alrededor de 34 estaciones del Tren Maya utilizando información del Directorio Estadístico Nacional de Unidades Económicas (DENUE).

El proyecto compara dos cortes temporales:

- DENUE noviembre 2019
- DENUE mayo 2025

El objetivo principal es responder:

> ¿Cómo cambió la actividad empresarial alrededor de las 34 estaciones del Tren Maya entre 2019 y 2025?

Los resultados representan cambios observados alrededor de las estaciones y no deben interpretarse como evidencia causal de que el Tren Maya haya creado o eliminado establecimientos.

---

## Arquitectura

```text
DENUE 2019 / 2025
        |
        v
Validación de datos
        |
        v
Normalización
        |
        v
Análisis geoespacial
        |
        v
Asignación a estación más cercana
        |
        v
Data Mart
        |
        v
PostgreSQL
        |
        v
Vistas analíticas
        |
        v
Power BI
