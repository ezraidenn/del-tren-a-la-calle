from pathlib import Path
import pandas as pd

MART_DIR = Path("data/mart")
OUTPUT_DIR = Path("data/analysis")
OUTPUT_FILE = OUTPUT_DIR / "state_change.csv"


def main():
    print("=" * 65)
    print("TREN MAYA - BUSINESS CHANGE BY STATE")
    print("=" * 65)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Load Data Mart
    # --------------------------------------------------
    fact = pd.read_parquet(MART_DIR / "fact_business.parquet")
    station = pd.read_parquet(MART_DIR / "dim_station.parquet")
    time = pd.read_parquet(MART_DIR / "dim_time.parquet")

    # --------------------------------------------------
    # Add descriptive dimensions
    # --------------------------------------------------
    df = (
        fact
        .merge(
            station[["station_key", "state"]],
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
    )

    # --------------------------------------------------
    # Aggregate
    # --------------------------------------------------
    state_year = (
        df.groupby(
            ["state", "snapshot_year"],
            as_index=False
        )["establishment_count"]
        .sum()
    )

    # Convert years to columns
    result = (
        state_year
        .pivot(
            index="state",
            columns="snapshot_year",
            values="establishment_count"
        )
        .fillna(0)
        .reset_index()
    )

    result.columns.name = None

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

    # Sort by absolute change
    result = result.sort_values(
        "absolute_change",
        ascending=False
    ).reset_index(drop=True)

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------
    total_2019 = int(result["businesses_2019"].sum())
    total_2025 = int(result["businesses_2025"].sum())
    total_change = int(result["absolute_change"].sum())

    if total_2019 != 39350:
        raise ValueError(
            f"2019 validation failed: {total_2019:,}"
        )

    if total_2025 != 44838:
        raise ValueError(
            f"2025 validation failed: {total_2025:,}"
        )

    if total_change != 5488:
        raise ValueError(
            f"Change validation failed: {total_change:,}"
        )

    # --------------------------------------------------
    # Export
    # --------------------------------------------------
    result.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    # --------------------------------------------------
    # Display
    # --------------------------------------------------
    display = result.copy()

    display["pct_change"] = display["pct_change"].map(
        lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A"
    )

    print("\nRESULTS BY STATE\n")
    print(display.to_string(index=False))

    print("\n" + "-" * 65)
    print(f"2019 total:      {total_2019:,}")
    print(f"2025 total:      {total_2025:,}")
    print(f"Absolute change: {total_change:+,}")
    print("-" * 65)

    print(f"\n[OK] Exported: {OUTPUT_FILE}")
    print("[OK] State analysis validation passed.")


if __name__ == "__main__":
    main()
