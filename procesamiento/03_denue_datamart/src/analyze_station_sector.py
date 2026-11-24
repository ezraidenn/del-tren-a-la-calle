from pathlib import Path
import pandas as pd

MART_DIR = Path("data/mart")
OUTPUT_DIR = Path("data/analysis")
OUTPUT_FILE = OUTPUT_DIR / "station_sector_change.csv"


def main():
    print("=" * 75)
    print("TREN MAYA - BUSINESS CHANGE BY STATION AND SECTOR")
    print("=" * 75)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Load Data Mart
    # --------------------------------------------------
    fact = pd.read_parquet(MART_DIR / "fact_business.parquet")
    station = pd.read_parquet(MART_DIR / "dim_station.parquet")
    time = pd.read_parquet(MART_DIR / "dim_time.parquet")
    activity = pd.read_parquet(MART_DIR / "dim_activity.parquet")

    # --------------------------------------------------
    # Join dimensions
    # --------------------------------------------------
    df = (
        fact
        .merge(
            station[
                ["station_key", "station_id", "station_name", "state"]
            ],
            on="station_key",
            how="left",
            validate="many_to_one",
        )
        .merge(
            time[["time_key", "snapshot_year"]],
            on="time_key",
            how="left",
            validate="many_to_one",
        )
        .merge(
            activity[
                ["activity_key", "sector_code", "sector_name"]
            ],
            on="activity_key",
            how="left",
            validate="many_to_one",
        )
    )

    # --------------------------------------------------
    # Aggregate station + sector + year
    # --------------------------------------------------
    grouped = (
        df.groupby(
            [
                "station_id",
                "station_name",
                "state",
                "sector_code",
                "sector_name",
                "snapshot_year",
            ],
            as_index=False,
            dropna=False,
        )["establishment_count"]
        .sum()
    )

    # --------------------------------------------------
    # Pivot years
    # --------------------------------------------------
    result = (
        grouped.pivot_table(
            index=[
                "station_id",
                "station_name",
                "state",
                "sector_code",
                "sector_name",
            ],
            columns="snapshot_year",
            values="establishment_count",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    result.columns.name = None

    if 2019 not in result.columns:
        result[2019] = 0

    if 2025 not in result.columns:
        result[2025] = 0

    result = result.rename(
        columns={
            2019: "businesses_2019",
            2025: "businesses_2025",
        }
    )

    # --------------------------------------------------
    # Calculate change
    # --------------------------------------------------
    result["absolute_change"] = (
        result["businesses_2025"]
        - result["businesses_2019"]
    )

    result["pct_change"] = (
        result["absolute_change"]
        .div(result["businesses_2019"].replace(0, pd.NA))
        .mul(100)
    )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------
    total_2019 = int(result["businesses_2019"].sum())
    total_2025 = int(result["businesses_2025"].sum())
    total_change = int(result["absolute_change"].sum())

    assert total_2019 == 39350, (
        f"2019 validation failed: {total_2019:,}"
    )

    assert total_2025 == 44838, (
        f"2025 validation failed: {total_2025:,}"
    )

    assert total_change == 5488, (
        f"Change validation failed: {total_change:,}"
    )

    # --------------------------------------------------
    # Sort and export
    # --------------------------------------------------
    result = result.sort_values(
        ["station_name", "absolute_change"],
        ascending=[True, False],
    ).reset_index(drop=True)

    result.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Show strongest positive contributions
    # --------------------------------------------------
    positive = (
        result[result["absolute_change"] > 0]
        .sort_values("absolute_change", ascending=False)
        .head(15)
        .copy()
    )

    print("\nTOP 15 POSITIVE STATION-SECTOR CHANGES\n")

    print(
        positive[
            [
                "station_name",
                "state",
                "sector_code",
                "sector_name",
                "businesses_2019",
                "businesses_2025",
                "absolute_change",
                "pct_change",
            ]
        ].to_string(
            index=False,
            formatters={
                "pct_change": lambda x: (
                    f"{x:+.2f}%"
                    if pd.notna(x)
                    else "N/A"
                )
            },
        )
    )

    # --------------------------------------------------
    # Show strongest negative contributions
    # --------------------------------------------------
    negative = (
        result[result["absolute_change"] < 0]
        .sort_values("absolute_change")
        .head(10)
        .copy()
    )

    print("\nTOP 10 NEGATIVE STATION-SECTOR CHANGES\n")

    print(
        negative[
            [
                "station_name",
                "state",
                "sector_code",
                "sector_name",
                "businesses_2019",
                "businesses_2025",
                "absolute_change",
                "pct_change",
            ]
        ].to_string(
            index=False,
            formatters={
                "pct_change": lambda x: (
                    f"{x:+.2f}%"
                    if pd.notna(x)
                    else "N/A"
                )
            },
        )
    )

    print("\n" + "-" * 75)
    print(f"2019 total:      {total_2019:,}")
    print(f"2025 total:      {total_2025:,}")
    print(f"Absolute change: {total_change:+,}")
    print("-" * 75)

    print(f"\n[OK] Exported: {OUTPUT_FILE}")
    print("[OK] Station-sector analysis validation passed.")


if __name__ == "__main__":
    main()
