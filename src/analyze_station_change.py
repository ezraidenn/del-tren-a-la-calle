from pathlib import Path
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"

YEARS = [2019, 2025]
BANDS = ["0-1 km", "1-3 km", "3-5 km"]


def load_year(year):
    path = PROCESSED / f"denue_{year}_geospatial.parquet"

    df = pd.read_parquet(
        path,
        columns=[
            "nearest_station_id",
            "nearest_station_name",
            "distance_km",
            "distance_band",
            "snapshot_year"
        ]
    )

    # Solo negocios dentro de nuestros 5 km de análisis
    df = df[df["distance_km"] <= 5].copy()

    return df


def main():

    print("=== CAMBIO EMPRESARIAL POR ESTACIÓN ===\n")

    frames = []

    for year in YEARS:
        df = load_year(year)

        print(
            f"{year}: {len(df):,} establecimientos <= 5 km"
        )

        frames.append(df)

    data = pd.concat(frames, ignore_index=True)

    # Conteo por estación, anillo y año
    grouped = (
        data
        .groupby(
            [
                "nearest_station_id",
                "nearest_station_name",
                "distance_band",
                "snapshot_year"
            ],
            observed=True
        )
        .size()
        .reset_index(name="establishments")
    )

    # Año como columnas
    pivot = (
        grouped
        .pivot_table(
            index=[
                "nearest_station_id",
                "nearest_station_name",
                "distance_band"
            ],
            columns="snapshot_year",
            values="establishments",
            fill_value=0
        )
        .reset_index()
    )

    pivot.columns.name = None

    # Asegurar que existan ambos años
    for year in YEARS:
        if year not in pivot.columns:
            pivot[year] = 0

    pivot = pivot.rename(
        columns={
            2019: "businesses_2019",
            2025: "businesses_2025"
        }
    )

    pivot["absolute_change"] = (
        pivot["businesses_2025"]
        - pivot["businesses_2019"]
    )

    pivot["pct_change"] = np.where(
        pivot["businesses_2019"] > 0,
        (
            pivot["absolute_change"]
            / pivot["businesses_2019"]
        ) * 100,
        np.nan
    )

    # Orden lógico de los anillos
    pivot["distance_band"] = pd.Categorical(
        pivot["distance_band"],
        categories=BANDS,
        ordered=True
    )

    pivot = pivot.sort_values(
        [
            "nearest_station_id",
            "distance_band"
        ]
    )

    output = PROCESSED / "station_ring_change_2019_2025.csv"

    pivot.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n=== RESULTADO GLOBAL <= 5 KM ===")

    total_2019 = int(pivot["businesses_2019"].sum())
    total_2025 = int(pivot["businesses_2025"].sum())

    difference = total_2025 - total_2019
    pct = (
        difference / total_2019 * 100
        if total_2019 else np.nan
    )

    print(f"2019: {total_2019:,}")
    print(f"2025: {total_2025:,}")
    print(f"Cambio absoluto: {difference:+,}")
    print(f"Cambio porcentual: {pct:+.2f}%")

    print("\n=== MAYORES CAMBIOS ABSOLUTOS ===")

    station_total = (
        pivot
        .groupby(
            [
                "nearest_station_id",
                "nearest_station_name"
            ],
            observed=True
        )[
            [
                "businesses_2019",
                "businesses_2025",
                "absolute_change"
            ]
        ]
        .sum()
        .reset_index()
    )

    station_total["pct_change"] = np.where(
        station_total["businesses_2019"] > 0,
        (
            station_total["absolute_change"]
            / station_total["businesses_2019"]
        ) * 100,
        np.nan
    )

    station_total = station_total.sort_values(
        "absolute_change",
        ascending=False
    )

    print(
        station_total[
            [
                "nearest_station_name",
                "businesses_2019",
                "businesses_2025",
                "absolute_change",
                "pct_change"
            ]
        ]
        .to_string(
            index=False,
            formatters={
                "pct_change": lambda x: f"{x:+.2f}%"
            }
        )
    )

    station_output = (
        PROCESSED
        / "station_total_change_2019_2025.csv"
    )

    station_total.to_csv(
        station_output,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nArchivos generados:")
    print(output)
    print(station_output)


if __name__ == "__main__":
    main()
