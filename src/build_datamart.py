from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
MART_DIR = PROJECT_ROOT / "data" / "mart"

STATIONS_FILE = (
    REFERENCE_DIR
    / "estaciones_tren_maya_catalogo_maestro.csv"
)

GEO_FILES = [
    PROCESSED_DIR / "denue_2019_geospatial.parquet",
    PROCESSED_DIR / "denue_2025_geospatial.parquet",
]

MART_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CARGA DE DATOS
# ============================================================

def load_business_data():

    frames = []

    for path in GEO_FILES:

        if not path.exists():
            raise FileNotFoundError(
                f"No existe el archivo: {path}"
            )

        df = pd.read_parquet(path)

        # El Data Mart utiliza solamente negocios
        # ubicados a máximo 5 km de una estación.
        df = df[
            df["distance_band"].isin(
                [
                    "0-1 km",
                    "1-3 km",
                    "3-5 km",
                ]
            )
        ].copy()

        frames.append(df)

    data = pd.concat(
        frames,
        ignore_index=True
    )

    return data


# ============================================================
# DIM_ESTACION
# ============================================================

def build_dim_station():

    stations = pd.read_csv(
        STATIONS_FILE
    )

    required = [
        "station_id",
        "station_name",
        "state",
        "municipality",
        "latitude",
        "longitude",
    ]

    missing = [
        column
        for column in required
        if column not in stations.columns
    ]

    if missing:
        raise ValueError(
            "Faltan columnas en catálogo de estaciones: "
            f"{missing}"
        )

    station = stations[
        required
    ].copy()

    station = (
        station
        .drop_duplicates(
            subset=["station_id"]
        )
        .sort_values("station_id")
        .reset_index(drop=True)
    )

    station.insert(
        0,
        "station_key",
        range(1, len(station) + 1)
    )

    return station


# ============================================================
# DIM_TIEMPO
# ============================================================

def build_dim_time():

    return pd.DataFrame(
        {
            "time_key": [
                1,
                2,
            ],
            "snapshot_year": [
                2019,
                2025,
            ],
        }
    )


# ============================================================
# DIM_DISTANCIA
# ============================================================

def build_dim_distance():

    return pd.DataFrame(
        {
            "distance_key": [
                1,
                2,
                3,
            ],
            "distance_band": [
                "0-1 km",
                "1-3 km",
                "3-5 km",
            ],
            "min_km": [
                0.0,
                1.0,
                3.0,
            ],
            "max_km": [
                1.0,
                3.0,
                5.0,
            ],
        }
    )


# ============================================================
# DIM_ACTIVIDAD
# ============================================================

def build_dim_activity(data):

    activity = data[
        [
            "codigo_act",
            "nombre_act",
        ]
    ].copy()

    activity["codigo_act"] = (
        activity["codigo_act"]
        .astype("string")
        .str.strip()
    )

    activity["nombre_act"] = (
        activity["nombre_act"]
        .astype("string")
        .str.strip()
    )

    activity = (
        activity
        .dropna(
            subset=["codigo_act"]
        )
        .drop_duplicates(
            subset=["codigo_act"],
            keep="first"
        )
        .sort_values("codigo_act")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Sector SCIAN
    # --------------------------------------------------------

    activity["sector_code"] = (
        activity["codigo_act"]
        .str[:2]
    )

    # --------------------------------------------------------
    # Nombre del sector
    # --------------------------------------------------------

    sector_names = {
        "11": (
            "Agricultura, cría y explotación de animales, "
            "aprovechamiento forestal, pesca y caza"
        ),

        "21": "Minería",

        "22": (
            "Generación, transmisión y distribución de "
            "energía eléctrica, agua y gas"
        ),

        "23": "Construcción",

        "31": "Industrias manufactureras",
        "32": "Industrias manufactureras",
        "33": "Industrias manufactureras",

        "43": "Comercio al por mayor",

        "46": "Comercio al por menor",

        "48": (
            "Transportes, correos y almacenamiento"
        ),

        "49": (
            "Transportes, correos y almacenamiento"
        ),

        "51": (
            "Información en medios masivos"
        ),

        "52": (
            "Servicios financieros y de seguros"
        ),

        "53": (
            "Servicios inmobiliarios y de alquiler "
            "de bienes muebles e intangibles"
        ),

        "54": (
            "Servicios profesionales, científicos "
            "y técnicos"
        ),

        "55": "Corporativos",

        "56": (
            "Servicios de apoyo a los negocios "
            "y manejo de residuos"
        ),

        "61": "Servicios educativos",

        "62": (
            "Servicios de salud y de asistencia social"
        ),

        "71": (
            "Servicios de esparcimiento culturales, "
            "deportivos y recreativos"
        ),

        "72": (
            "Servicios de alojamiento temporal "
            "y de preparación de alimentos y bebidas"
        ),

        "81": (
            "Otros servicios excepto actividades "
            "gubernamentales"
        ),

        "93": (
            "Actividades legislativas, "
            "gubernamentales y de impartición "
            "de justicia"
        ),
    }

    activity["sector_name"] = (
        activity["sector_code"]
        .map(sector_names)
        .fillna("No identificado")
    )

    activity.insert(
        0,
        "activity_key",
        range(1, len(activity) + 1)
    )

    return activity


# ============================================================
# DIM_ESTRATO DE PERSONAL
# ============================================================

def build_dim_employment(data):

    employment = (
        data[
            ["per_ocu"]
        ]
        .copy()
    )

    employment["per_ocu"] = (
        employment["per_ocu"]
        .astype("string")
        .str.strip()
    )

    employment = (
        employment
        .dropna(
            subset=["per_ocu"]
        )
        .drop_duplicates()
        .sort_values("per_ocu")
        .reset_index(drop=True)
    )

    employment = employment.rename(
        columns={
            "per_ocu":
            "employment_range"
        }
    )

    employment.insert(
        0,
        "employment_key",
        range(
            1,
            len(employment) + 1
        )
    )

    return employment


# ============================================================
# FACT_NEGOCIOS
# ============================================================

def build_fact(
    data,
    dim_station,
    dim_time,
    dim_distance,
    dim_activity,
    dim_employment,
):

    fact = data[
        [
            "nearest_station_id",
            "snapshot_year",
            "distance_band",
            "codigo_act",
            "per_ocu",
        ]
    ].copy()

    # --------------------------------------------------------
    # Normalización de tipos
    # --------------------------------------------------------

    fact["codigo_act"] = (
        fact["codigo_act"]
        .astype("string")
        .str.strip()
    )

    fact["per_ocu"] = (
        fact["per_ocu"]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------------------
    # Integrar claves sustitutas
    # --------------------------------------------------------

    fact = fact.merge(
        dim_station[
            [
                "station_key",
                "station_id",
            ]
        ],
        left_on="nearest_station_id",
        right_on="station_id",
        how="left",
        validate="many_to_one",
    )

    fact = fact.merge(
        dim_time[
            [
                "time_key",
                "snapshot_year",
            ]
        ],
        on="snapshot_year",
        how="left",
        validate="many_to_one",
    )

    fact = fact.merge(
        dim_distance[
            [
                "distance_key",
                "distance_band",
            ]
        ],
        on="distance_band",
        how="left",
        validate="many_to_one",
    )

    fact = fact.merge(
        dim_activity[
            [
                "activity_key",
                "codigo_act",
            ]
        ],
        on="codigo_act",
        how="left",
        validate="many_to_one",
    )

    fact = fact.merge(
        dim_employment[
            [
                "employment_key",
                "employment_range",
            ]
        ],
        left_on="per_ocu",
        right_on="employment_range",
        how="left",
        validate="many_to_one",
    )

    # --------------------------------------------------------
    # Validar claves
    # --------------------------------------------------------

    key_columns = [
        "station_key",
        "time_key",
        "distance_key",
        "activity_key",
        "employment_key",
    ]

    missing_keys = (
        fact[key_columns]
        .isna()
        .sum()
    )

    if missing_keys.sum() > 0:

        raise ValueError(
            "Se encontraron claves "
            "sin correspondencia:\n"
            f"{missing_keys}"
        )

    # --------------------------------------------------------
    # Agregación de la tabla de hechos
    #
    # Grano:
    # estación + año + distancia +
    # actividad + estrato de personal
    # --------------------------------------------------------

    fact = (
        fact
        .groupby(
            key_columns,
            observed=True,
        )
        .size()
        .reset_index(
            name="establishment_count"
        )
    )

    # Convertir claves a entero
    for column in key_columns:
        fact[column] = (
            fact[column]
            .astype("int64")
        )

    fact["establishment_count"] = (
        fact["establishment_count"]
        .astype("int64")
    )

    return fact


# ============================================================
# VALIDACIÓN DEL DATA MART
# ============================================================

def validate_mart(
    fact,
    dim_station,
    dim_time,
):

    print(
        "\n=== VALIDACIÓN DATA MART ==="
    )

    # --------------------------------------------------------
    # Número de estaciones
    # --------------------------------------------------------

    station_count = len(
        dim_station
    )

    print(
        "Estaciones en dimensión: "
        f"{station_count}"
    )

    if station_count != 34:
        raise ValueError(
            "Se esperaban 34 estaciones, "
            f"pero existen {station_count}."
        )

    # --------------------------------------------------------
    # Validación por año
    # --------------------------------------------------------

    validation = (
        fact
        .merge(
            dim_time,
            on="time_key",
            how="left",
            validate="many_to_one",
        )
        .groupby(
            "snapshot_year"
        )[
            "establishment_count"
        ]
        .sum()
    )

    expected = {
        2019: 39350,
        2025: 44838,
    }

    for year, expected_count in expected.items():

        actual = int(
            validation.get(
                year,
                0
            )
        )

        print(
            f"{year}: "
            f"{actual:,} establecimientos"
        )

        if actual != expected_count:

            raise ValueError(
                f"Validación fallida para "
                f"{year}: "
                f"esperado={expected_count:,}, "
                f"obtenido={actual:,}"
            )

    # --------------------------------------------------------
    # Total
    # --------------------------------------------------------

    total = int(
        fact[
            "establishment_count"
        ].sum()
    )

    print(
        "TOTAL: "
        f"{total:,}"
    )

    if total != 84188:
        raise ValueError(
            "Total incorrecto: "
            f"{total:,}"
        )

    # --------------------------------------------------------
    # Duplicados en el grano
    # --------------------------------------------------------

    grain = [
        "station_key",
        "time_key",
        "distance_key",
        "activity_key",
        "employment_key",
    ]

    duplicates = (
        fact
        .duplicated(
            subset=grain
        )
        .sum()
    )

    if duplicates != 0:
        raise ValueError(
            "La tabla de hechos contiene "
            f"{duplicates} combinaciones duplicadas."
        )

    print(
        "Filas agregadas FACT_NEGOCIOS: "
        f"{len(fact):,}"
    )

    print(
        "Integridad: OK"
    )


# ============================================================
# GUARDAR TABLA
# ============================================================

def save_table(
    dataframe,
    filename,
):

    output = (
        MART_DIR
        / filename
    )

    dataframe.to_parquet(
        output,
        index=False
    )

    print(
        f"{filename}: "
        f"{len(dataframe):,} filas"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=== CONSTRUCCIÓN DATA MART ==="
    )

    data = load_business_data()

    print(
        "Registros fuente <=5 km: "
        f"{len(data):,}"
    )

    # --------------------------------------------------------
    # Construcción de dimensiones
    # --------------------------------------------------------

    dim_station = (
        build_dim_station()
    )

    dim_time = (
        build_dim_time()
    )

    dim_distance = (
        build_dim_distance()
    )

    dim_activity = (
        build_dim_activity(data)
    )

    dim_employment = (
        build_dim_employment(data)
    )

    # --------------------------------------------------------
    # Construcción de FACT
    # --------------------------------------------------------

    fact = build_fact(
        data,
        dim_station,
        dim_time,
        dim_distance,
        dim_activity,
        dim_employment,
    )

    # --------------------------------------------------------
    # Validación
    # --------------------------------------------------------

    validate_mart(
        fact,
        dim_station,
        dim_time,
    )

    # --------------------------------------------------------
    # Guardar tablas
    # --------------------------------------------------------

    print(
        "\n=== GUARDANDO TABLAS ==="
    )

    save_table(
        dim_station,
        "dim_station.parquet"
    )

    save_table(
        dim_time,
        "dim_time.parquet"
    )

    save_table(
        dim_distance,
        "dim_distance.parquet"
    )

    save_table(
        dim_activity,
        "dim_activity.parquet"
    )

    save_table(
        dim_employment,
        "dim_employment.parquet"
    )

    save_table(
        fact,
        "fact_business.parquet"
    )

    print(
        "\nData Mart construido correctamente."
    )


if __name__ == "__main__":
    main()
