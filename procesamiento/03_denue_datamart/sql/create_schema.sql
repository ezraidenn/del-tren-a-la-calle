-- ==========================================================
-- TREN MAYA DATA MART
-- ESQUEMA ESTRELLA
-- DENUE 2019 vs 2025
-- ==========================================================

BEGIN;


-- ==========================================================
-- DIMENSIÓN: ESTACIÓN
-- ==========================================================

CREATE TABLE dim_station (
    station_key INTEGER PRIMARY KEY,
    station_id VARCHAR(10) NOT NULL UNIQUE,
    station_name VARCHAR(150) NOT NULL,
    state VARCHAR(100) NOT NULL,
    municipality VARCHAR(150),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);


-- ==========================================================
-- DIMENSIÓN: TIEMPO
-- ==========================================================

CREATE TABLE dim_time (
    time_key INTEGER PRIMARY KEY,
    snapshot_year INTEGER NOT NULL UNIQUE
);


-- ==========================================================
-- DIMENSIÓN: DISTANCIA
-- ==========================================================

CREATE TABLE dim_distance (
    distance_key INTEGER PRIMARY KEY,
    distance_band VARCHAR(20) NOT NULL UNIQUE,
    min_km NUMERIC(5,2) NOT NULL,
    max_km NUMERIC(5,2) NOT NULL,

    CONSTRAINT chk_distance_range
        CHECK (
            min_km >= 0
            AND max_km > min_km
        )
);


-- ==========================================================
-- DIMENSIÓN: ACTIVIDAD ECONÓMICA
-- ==========================================================

CREATE TABLE dim_activity (
    activity_key INTEGER PRIMARY KEY,

    codigo_act VARCHAR(20) NOT NULL UNIQUE,

    nombre_act TEXT,

    sector_code VARCHAR(2),

    sector_name VARCHAR(200)
);


-- ==========================================================
-- DIMENSIÓN: ESTRATO DE PERSONAL
-- ==========================================================

CREATE TABLE dim_employment (
    employment_key INTEGER PRIMARY KEY,

    employment_range VARCHAR(100)
        NOT NULL UNIQUE
);


-- ==========================================================
-- TABLA DE HECHOS: NEGOCIOS
--
-- Grano:
-- estación + año + anillo de distancia
-- + actividad SCIAN + estrato de personal
-- ==========================================================

CREATE TABLE fact_business (
    station_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    distance_key INTEGER NOT NULL,
    activity_key INTEGER NOT NULL,
    employment_key INTEGER NOT NULL,

    establishment_count INTEGER NOT NULL,

    CONSTRAINT pk_fact_business
        PRIMARY KEY (
            station_key,
            time_key,
            distance_key,
            activity_key,
            employment_key
        ),

    CONSTRAINT fk_fact_station
        FOREIGN KEY (station_key)
        REFERENCES dim_station(station_key),

    CONSTRAINT fk_fact_time
        FOREIGN KEY (time_key)
        REFERENCES dim_time(time_key),

    CONSTRAINT fk_fact_distance
        FOREIGN KEY (distance_key)
        REFERENCES dim_distance(distance_key),

    CONSTRAINT fk_fact_activity
        FOREIGN KEY (activity_key)
        REFERENCES dim_activity(activity_key),

    CONSTRAINT fk_fact_employment
        FOREIGN KEY (employment_key)
        REFERENCES dim_employment(employment_key),

    CONSTRAINT chk_establishment_count
        CHECK (establishment_count > 0)
);


-- ==========================================================
-- ÍNDICES PARA CONSULTAS ANALÍTICAS
-- ==========================================================

CREATE INDEX idx_fact_station
    ON fact_business(station_key);

CREATE INDEX idx_fact_time
    ON fact_business(time_key);

CREATE INDEX idx_fact_distance
    ON fact_business(distance_key);

CREATE INDEX idx_fact_activity
    ON fact_business(activity_key);

CREATE INDEX idx_fact_employment
    ON fact_business(employment_key);


COMMIT;
