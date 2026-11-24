-- ==========================================================
-- TREN MAYA DATA MART
-- VISTAS ANALÍTICAS PARA POWER BI
-- ==========================================================


-- ==========================================================
-- VISTA PRINCIPAL
--
-- Grano:
-- estación + año + anillo + actividad SCIAN
-- + estrato de personal
-- ==========================================================

CREATE OR REPLACE VIEW vw_business_analysis AS

SELECT
    -- Estación
    s.station_key,
    s.station_id,
    s.station_name,
    s.state,
    s.municipality,
    s.latitude,
    s.longitude,

    -- Tiempo
    t.time_key,
    t.snapshot_year,

    -- Distancia
    d.distance_key,
    d.distance_band,
    d.min_km,
    d.max_km,

    -- Actividad económica
    a.activity_key,
    a.codigo_act,
    a.nombre_act,
    a.sector_code,
    a.sector_name,

    -- Estrato de personal
    e.employment_key,
    e.employment_range,

    -- Medida
    f.establishment_count

FROM fact_business f

JOIN dim_station s
    ON f.station_key = s.station_key

JOIN dim_time t
    ON f.time_key = t.time_key

JOIN dim_distance d
    ON f.distance_key = d.distance_key

JOIN dim_activity a
    ON f.activity_key = a.activity_key

JOIN dim_employment e
    ON f.employment_key = e.employment_key;
-- ==========================================================
-- VISTA COMPARATIVA POR ESTACIÓN
-- 2019 vs 2025
-- ==========================================================

CREATE OR REPLACE VIEW vw_station_change AS

WITH station_year AS (

    SELECT
        s.station_key,
        s.station_id,
        s.station_name,
        s.state,
        s.municipality,
        s.latitude,
        s.longitude,
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
        s.station_key,
        s.station_id,
        s.station_name,
        s.state,
        s.municipality,
        s.latitude,
        s.longitude,
        t.snapshot_year
),

comparison AS (

    SELECT
        station_key,
        station_id,
        station_name,
        state,
        municipality,
        latitude,
        longitude,

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
        station_key,
        station_id,
        station_name,
        state,
        municipality,
        latitude,
        longitude
)

SELECT
    station_key,
    station_id,
    station_name,
    state,
    municipality,
    latitude,
    longitude,

    businesses_2019,
    businesses_2025,

    businesses_2025
        - businesses_2019
        AS absolute_change,

    ROUND(
        (
            businesses_2025
            - businesses_2019
        )::numeric
        / NULLIF(
            businesses_2019,
            0
        )
        * 100,
        2
    ) AS pct_change

FROM comparison;
-- ==========================================================
-- VISTA COMPARATIVA POR SECTOR SCIAN
-- 2019 vs 2025
-- ==========================================================

CREATE OR REPLACE VIEW vw_sector_change AS

WITH sector_year AS (

    SELECT
        a.sector_code,
        a.sector_name,
        t.snapshot_year,
        SUM(f.establishment_count) AS businesses

    FROM fact_business f

    JOIN dim_activity a
        ON f.activity_key = a.activity_key

    JOIN dim_time t
        ON f.time_key = t.time_key

    GROUP BY
        a.sector_code,
        a.sector_name,
        t.snapshot_year
),

comparison AS (

    SELECT
        sector_code,
        sector_name,

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
        sector_code,
        sector_name
)

SELECT
    sector_code,
    sector_name,
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
-- VISTA COMPARATIVA POR ANILLO DE DISTANCIA
-- 2019 vs 2025
-- ==========================================================

CREATE OR REPLACE VIEW vw_distance_change AS

WITH distance_year AS (

    SELECT
        d.distance_key,
        d.distance_band,
        d.min_km,
        d.max_km,
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
        d.min_km,
        d.max_km,
        t.snapshot_year
),

comparison AS (

    SELECT
        distance_key,
        distance_band,
        min_km,
        max_km,

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

    FROM distance_year

    GROUP BY
        distance_key,
        distance_band,
        min_km,
        max_km
)

SELECT
    distance_key,
    distance_band,
    min_km,
    max_km,

    businesses_2019,
    businesses_2025,

    businesses_2025
        - businesses_2019
        AS absolute_change,

    ROUND(
        (
            businesses_2025
            - businesses_2019
        )::numeric
        / NULLIF(
            businesses_2019,
            0
        )
        * 100,
        2
    ) AS pct_change

FROM comparison;
