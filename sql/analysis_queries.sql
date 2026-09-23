-- ==========================================================
-- TREN MAYA DATA MART
-- CONSULTAS ANALÍTICAS
-- DENUE 2019 vs 2025
-- ==========================================================


-- ==========================================================
-- KPI 1
-- Total de establecimientos y variación 2019-2025
-- ==========================================================

WITH totals AS (
    SELECT
        t.snapshot_year,
        SUM(f.establishment_count) AS businesses

    FROM fact_business f

    JOIN dim_time t
        ON f.time_key = t.time_key

    GROUP BY
        t.snapshot_year
),

comparison AS (
    SELECT
        MAX(
            CASE
                WHEN snapshot_year = 2019
                THEN businesses
            END
        ) AS businesses_2019,

        MAX(
            CASE
                WHEN snapshot_year = 2025
                THEN businesses
            END
        ) AS businesses_2025

    FROM totals
)

SELECT
    businesses_2019,
    businesses_2025,

    businesses_2025 - businesses_2019
        AS absolute_change,

    ROUND(
        (
            businesses_2025 - businesses_2019
        )::numeric
        / NULLIF(businesses_2019, 0)
        * 100,
        2
    ) AS pct_change

FROM comparison;


-- ==========================================================
-- KPI 2
-- Cambio de establecimientos por estación
-- Incluye las 34 estaciones, incluso aquellas con 0 negocios
-- ==========================================================

WITH station_year AS (
    SELECT
        s.station_id,
        s.station_name,
        t.snapshot_year,

        COALESCE(
            SUM(f.establishment_count),
            0
        ) AS businesses

    FROM dim_station s

    CROSS JOIN dim_time t

    LEFT JOIN fact_business f
        ON f.station_key = s.station_key
        AND f.time_key = t.time_key

    GROUP BY
        s.station_id,
        s.station_name,
        t.snapshot_year
),

station_comparison AS (
    SELECT
        station_id,
        station_name,

        MAX(
            CASE
                WHEN snapshot_year = 2019
                THEN businesses
            END
        ) AS businesses_2019,

        MAX(
            CASE
                WHEN snapshot_year = 2025
                THEN businesses
            END
        ) AS businesses_2025

    FROM station_year

    GROUP BY
        station_id,
        station_name
)

SELECT
    station_id,
    station_name,
    businesses_2019,
    businesses_2025,

    businesses_2025 - businesses_2019
        AS absolute_change,

    ROUND(
        (
            businesses_2025 - businesses_2019
        )::numeric
        / NULLIF(businesses_2019, 0)
        * 100,
        2
    ) AS pct_change

FROM station_comparison

ORDER BY
    absolute_change DESC,
    station_name;


-- ==========================================================
-- KPI 3
-- Cambio de establecimientos por anillo de distancia
-- 0-1 km / 1-3 km / 3-5 km
-- ==========================================================

WITH ring_year AS (
    SELECT
        d.distance_key,
        d.distance_band,
        t.snapshot_year,

        SUM(
            f.establishment_count
        ) AS businesses

    FROM fact_business f

    JOIN dim_distance d
        ON f.distance_key = d.distance_key

    JOIN dim_time t
        ON f.time_key = t.time_key

    GROUP BY
        d.distance_key,
        d.distance_band,
        t.snapshot_year
),

ring_comparison AS (
    SELECT
        distance_key,
        distance_band,

        MAX(
            CASE
                WHEN snapshot_year = 2019
                THEN businesses
            END
        ) AS businesses_2019,

        MAX(
            CASE
                WHEN snapshot_year = 2025
                THEN businesses
            END
        ) AS businesses_2025

    FROM ring_year

    GROUP BY
        distance_key,
        distance_band
)

SELECT
    distance_band,
    businesses_2019,
    businesses_2025,

    businesses_2025 - businesses_2019
        AS absolute_change,

    ROUND(
        (
            businesses_2025 - businesses_2019
        )::numeric
        / NULLIF(businesses_2019, 0)
        * 100,
        2
    ) AS pct_change

FROM ring_comparison

ORDER BY
    distance_key;
-- ==========================================================
-- KPI 4
-- Cambio de establecimientos por sector económico SCIAN
-- ==========================================================

WITH sector_year AS (
    SELECT
        a.sector_code,
        t.snapshot_year,
        SUM(f.establishment_count) AS businesses

    FROM fact_business f

    JOIN dim_activity a
        ON f.activity_key = a.activity_key

    JOIN dim_time t
        ON f.time_key = t.time_key

    GROUP BY
        a.sector_code,
        t.snapshot_year
),

sector_comparison AS (
    SELECT
        sector_code,

        COALESCE(
            MAX(
                CASE
                    WHEN snapshot_year = 2019
                    THEN businesses
                END
            ),
            0
        ) AS businesses_2019,

        COALESCE(
            MAX(
                CASE
                    WHEN snapshot_year = 2025
                    THEN businesses
                END
            ),
            0
        ) AS businesses_2025

    FROM sector_year

    GROUP BY
        sector_code
)

SELECT
    sector_code,
    businesses_2019,
    businesses_2025,

    businesses_2025 - businesses_2019
        AS absolute_change,

    ROUND(
        (
            businesses_2025 - businesses_2019
        )::numeric
        / NULLIF(businesses_2019, 0)
        * 100,
        2
    ) AS pct_change

FROM sector_comparison

ORDER BY
    absolute_change DESC;
