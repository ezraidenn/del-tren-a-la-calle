from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
STATIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "estaciones_tren_maya_catalogo_maestro.csv"
)

EARTH_RADIUS_KM = 6371.0088


def load_stations():
    stations = pd.read_csv(STATIONS_FILE)

    required = {
        "station_id",
        "station_name",
        "state",
        "municipality",
        "latitude",
        "longitude",
    }

    missing = required - set(stations.columns)

    if missing:
        raise ValueError(
            f"Faltan columnas en catálogo de estaciones: {missing}"
        )

    if stations["station_id"].duplicated().any():
        raise ValueError("Hay station_id duplicados.")

    if stations[["latitude", "longitude"]].isna().any().any():
        raise ValueError("Hay coordenadas nulas en estaciones.")

    return stations


def create_tree(stations):
    station_coordinates = np.radians(
        stations[["latitude", "longitude"]].to_numpy()
    )

    return BallTree(
        station_coordinates,
        metric="haversine"
    )


def classify_distance(distance):
    return pd.cut(
        distance,
        bins=[-np.inf, 1, 3, 5, np.inf],
        labels=[
            "0-1 km",
            "1-3 km",
            "3-5 km",
            ">5 km"
        ],
        right=True
    )


def match_year(year, stations, tree):

    input_file = (
        PROCESSED_DIR
        / f"denue_{year}_normalized.parquet"
    )

    print(f"\nProcesando {year}...")

    df = pd.read_parquet(input_file)

    valid_mask = (
        df["latitud"].notna()
        & df["longitud"].notna()
        & df["latitud"].between(-90, 90)
        & df["longitud"].between(-180, 180)
    )

    valid = df.loc[valid_mask].copy()
    invalid = df.loc[~valid_mask].copy()

    print(f"Registros totales: {len(df):,}")
    print(f"Coordenadas válidas: {len(valid):,}")
    print(f"Coordenadas inválidas: {len(invalid):,}")

    business_coordinates = np.radians(
        valid[["latitud", "longitud"]].to_numpy()
    )

    distances, indices = tree.query(
        business_coordinates,
        k=1
    )

    valid["distance_km"] = (
        distances[:, 0] * EARTH_RADIUS_KM
    )

    nearest_indices = indices[:, 0]

    valid["nearest_station_id"] = (
        stations.iloc[nearest_indices]["station_id"]
        .to_numpy()
    )

    valid["nearest_station_name"] = (
        stations.iloc[nearest_indices]["station_name"]
        .to_numpy()
    )

    valid["station_state"] = (
        stations.iloc[nearest_indices]["state"]
        .to_numpy()
    )

    valid["distance_band"] = classify_distance(
        valid["distance_km"]
    )

    # Registros sin coordenadas permanecen en el dataset,
    # pero no reciben asignación espacial.
    invalid["distance_km"] = np.nan
    invalid["nearest_station_id"] = pd.NA
    invalid["nearest_station_name"] = pd.NA
    invalid["station_state"] = pd.NA
    invalid["distance_band"] = pd.NA

    result = pd.concat(
        [valid, invalid],
        ignore_index=True
    )

    # Garantizar que no perdimos ni duplicamos registros.
    if len(result) != len(df):
        raise RuntimeError(
            "El número de registros cambió durante el matching."
        )

    output_file = (
        PROCESSED_DIR
        / f"denue_{year}_geospatial.parquet"
    )

    result.to_parquet(
        output_file,
        index=False
    )

    print("\nDistribución por distancia:")
    print(
        result["distance_band"]
        .value_counts(dropna=False)
        .reindex(
            ["0-1 km", "1-3 km", "3-5 km", ">5 km"]
        )
    )

    within_5km = (
        result["distance_km"].le(5).sum()
    )

    print(
        f"\nEstablecimientos <= 5 km: "
        f"{within_5km:,}"
    )

    print(
        f"Archivo generado:\n{output_file}"
    )

    return result


def main():

    print("=== GEOESPACIAL DENUE / TREN MAYA ===")

    stations = load_stations()

    print(
        f"Estaciones cargadas: {len(stations)}"
    )

    tree = create_tree(stations)

    totals = {}

    for year in [2019, 2025]:

        result = match_year(
            year,
            stations,
            tree
        )

        totals[year] = len(result)

    print("\n=== VALIDACIÓN FINAL ===")

    for year, total in totals.items():
        print(
            f"{year}: {total:,} registros conservados"
        )

    print(
        f"TOTAL: {sum(totals.values()):,}"
    )

    print("\nMatching geoespacial completado.")


if __name__ == "__main__":
    main()
