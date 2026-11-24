from pathlib import Path
import pandas as pd

MART_DIR = Path("data/mart")

EXPECTED_ROWS = {
    "dim_station": 34,
    "dim_time": 2,
    "dim_distance": 3,
    "dim_activity": 717,
    "dim_employment": 7,
    "fact_business": 18061,
}

EXPECTED_TOTALS = {
    2019: 39350,
    2025: 44838,
}

PRIMARY_KEYS = {
    "dim_station": "station_key",
    "dim_time": "time_key",
    "dim_distance": "distance_key",
    "dim_activity": "activity_key",
    "dim_employment": "employment_key",
}

RELATIONSHIPS = {
    "station_key": ("dim_station", "station_key"),
    "time_key": ("dim_time", "time_key"),
    "distance_key": ("dim_distance", "distance_key"),
    "activity_key": ("dim_activity", "activity_key"),
    "employment_key": ("dim_employment", "employment_key"),
}


def check(condition, message):
    if condition:
        print(f"[OK] {message}")
        return True

    print(f"[ERROR] {message}")
    return False


def main():
    print("=" * 60)
    print("TREN MAYA DATA MART - FINAL VALIDATION")
    print("=" * 60)

    all_ok = True
    tables = {}

    # ------------------------------------------------------
    # 1. Files and row counts
    # ------------------------------------------------------
    print("\n1. FILES AND ROW COUNTS")

    for table, expected_rows in EXPECTED_ROWS.items():
        path = MART_DIR / f"{table}.parquet"

        if not path.exists():
            print(f"[ERROR] Missing file: {path}")
            all_ok = False
            continue

        df = pd.read_parquet(path)
        tables[table] = df

        all_ok &= check(
            len(df) == expected_rows,
            f"{table}: {len(df):,} rows "
            f"(expected {expected_rows:,})"
        )

    if len(tables) != len(EXPECTED_ROWS):
        print("\nFINAL RESULT: DATA MART VALIDATION FAILED")
        raise SystemExit(1)

    fact = tables["fact_business"]

    # ------------------------------------------------------
    # 2. Dimension primary keys
    # ------------------------------------------------------
    print("\n2. DIMENSION PRIMARY KEYS")

    for table, key in PRIMARY_KEYS.items():
        df = tables[table]

        all_ok &= check(
            key in df.columns,
            f"{table}.{key} exists"
        )

        if key not in df.columns:
            continue

        all_ok &= check(
            df[key].isna().sum() == 0,
            f"{table}.{key}: no NULL values"
        )

        all_ok &= check(
            df[key].duplicated().sum() == 0,
            f"{table}.{key}: unique"
        )

    # ------------------------------------------------------
    # 3. Fact-table required columns and NULLs
    # ------------------------------------------------------
    print("\n3. FACT TABLE VALIDATION")

    required_fact_columns = [
        "station_key",
        "time_key",
        "distance_key",
        "activity_key",
        "employment_key",
        "establishment_count",
    ]

    for column in required_fact_columns:
        all_ok &= check(
            column in fact.columns,
            f"fact_business.{column} exists"
        )

        if column in fact.columns:
            all_ok &= check(
                fact[column].isna().sum() == 0,
                f"fact_business.{column}: no NULL values"
            )

    # ------------------------------------------------------
    # 4. Fact-table grain
    # ------------------------------------------------------
    print("\n4. FACT TABLE GRAIN")

    grain = [
        "station_key",
        "time_key",
        "distance_key",
        "activity_key",
        "employment_key",
    ]

    duplicate_count = fact.duplicated(subset=grain).sum()

    all_ok &= check(
        duplicate_count == 0,
        f"No duplicate grain rows (duplicates: {duplicate_count:,})"
    )

    # ------------------------------------------------------
    # 5. Foreign keys
    # ------------------------------------------------------
    print("\n5. FOREIGN KEY VALIDATION")

    for fact_key, (dimension, dimension_key) in RELATIONSHIPS.items():
        dimension_values = set(tables[dimension][dimension_key])
        fact_values = set(fact[fact_key])

        missing = fact_values - dimension_values

        all_ok &= check(
            len(missing) == 0,
            f"fact_business.{fact_key} -> "
            f"{dimension}.{dimension_key}"
        )

    # ------------------------------------------------------
    # 6. Measure validation
    # ------------------------------------------------------
    print("\n6. MEASURE VALIDATION")

    all_ok &= check(
        (fact["establishment_count"] > 0).all(),
        "All establishment_count values are positive"
    )

    # ------------------------------------------------------
    # 7. Totals by year
    # ------------------------------------------------------
    print("\n7. ESTABLISHMENT TOTALS")

    fact_with_year = fact.merge(
        tables["dim_time"][["time_key", "snapshot_year"]],
        on="time_key",
        how="left",
        validate="many_to_one",
    )

    all_ok &= check(
        fact_with_year["snapshot_year"].isna().sum() == 0,
        "All fact rows resolve to a snapshot year"
    )

    totals = (
        fact_with_year
        .groupby("snapshot_year")["establishment_count"]
        .sum()
        .to_dict()
    )

    for year, expected in EXPECTED_TOTALS.items():
        actual = int(totals.get(year, 0))

        all_ok &= check(
            actual == expected,
            f"{year}: {actual:,} establishments "
            f"(expected {expected:,})"
        )

    grand_total = int(fact["establishment_count"].sum())

    all_ok &= check(
        grand_total == 84188,
        f"Grand total: {grand_total:,} establishments "
        "(expected 84,188)"
    )

    # ------------------------------------------------------
    # 8. Business-rule validation
    # ------------------------------------------------------
    print("\n8. BUSINESS RULE VALIDATION")

    station_ids = tables["dim_station"]["station_id"]

    all_ok &= check(
        station_ids.isna().sum() == 0,
        "All stations have station_id"
    )

    all_ok &= check(
        station_ids.nunique() == 34,
        "34 unique station IDs"
    )

    distance_bands = set(
        tables["dim_distance"]["distance_band"].astype(str)
    )

    expected_bands = {
        "0-1 km",
        "1-3 km",
        "3-5 km",
    }

    all_ok &= check(
        distance_bands == expected_bands,
        "Distance bands are exactly 0-1 km, 1-3 km and 3-5 km"
    )

    years = set(
        tables["dim_time"]["snapshot_year"]
        .astype(int)
        .tolist()
    )

    all_ok &= check(
        years == {2019, 2025},
        "Time dimension contains exactly 2019 and 2025"
    )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------
    print("\n" + "=" * 60)

    if all_ok:
        print("FINAL RESULT: DATA MART VALIDATION PASSED")
        print("=" * 60)
        raise SystemExit(0)

    print("FINAL RESULT: DATA MART VALIDATION FAILED")
    print("=" * 60)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
