from pathlib import Path
import getpass

import pandas as pd
import psycopg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MART = PROJECT_ROOT / "data" / "mart"

DB_NAME = "tren_maya_datamart"
DB_USER = "trenmaya_user"
DB_HOST = "localhost"
DB_PORT = 5432

TABLES = [
    "dim_station",
    "dim_time",
    "dim_distance",
    "dim_activity",
    "dim_employment",
    "fact_business",
]


def load_parquet(table_name):
    path = MART / f"{table_name}.parquet"

    if not path.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {path}"
        )

    return pd.read_parquet(path)


def main():

    print("=== CARGA DATA MART -> POSTGRESQL ===\n")

    password = getpass.getpass(
        "Contraseña de trenmaya_user: "
    )

    conninfo = (
        f"host={DB_HOST} "
        f"port={DB_PORT} "
        f"dbname={DB_NAME} "
        f"user={DB_USER} "
        f"password={password}"
    )

    with psycopg.connect(conninfo) as conn:

        print("Conexión PostgreSQL: OK\n")

        # Orden inverso para limpiar respetando FK.
        with conn.cursor() as cur:
            cur.execute("DELETE FROM fact_business;")
            cur.execute("DELETE FROM dim_employment;")
            cur.execute("DELETE FROM dim_activity;")
            cur.execute("DELETE FROM dim_distance;")
            cur.execute("DELETE FROM dim_time;")
            cur.execute("DELETE FROM dim_station;")

        print("Tablas preparadas para carga.\n")

        for table in TABLES:

            df = load_parquet(table)

            columns = list(df.columns)

            column_sql = ", ".join(
                f'"{col}"' for col in columns
            )

            placeholders = ", ".join(
                ["%s"] * len(columns)
            )

            sql = (
                f'INSERT INTO "{table}" '
                f'({column_sql}) '
                f'VALUES ({placeholders})'
            )

            rows = [
                tuple(
                    None if pd.isna(value) else value
                    for value in row
                )
                for row in df.itertuples(
                    index=False,
                    name=None
                )
            ]

            with conn.cursor() as cur:
                cur.executemany(sql, rows)

            print(
                f"{table}: "
                f"{len(df):,} filas cargadas"
            )

        conn.commit()

        print("\n=== VALIDACIÓN POSTGRESQL ===")

        with conn.cursor() as cur:

            for table in TABLES:

                cur.execute(
                    f'SELECT COUNT(*) FROM "{table}"'
                )

                count = cur.fetchone()[0]

                print(
                    f"{table}: {count:,} filas"
                )

            cur.execute("""
                SELECT
                    t.snapshot_year,
                    SUM(f.establishment_count)
                FROM fact_business f
                JOIN dim_time t
                    ON f.time_key = t.time_key
                GROUP BY t.snapshot_year
                ORDER BY t.snapshot_year;
            """)

            totals = cur.fetchall()

            print("\nEstablecimientos por año:")

            for year, total in totals:
                print(
                    f"{year}: {total:,}"
                )

            cur.execute("""
                SELECT
                    SUM(establishment_count)
                FROM fact_business;
            """)

            grand_total = cur.fetchone()[0]

            print(
                f"\nTOTAL: {grand_total:,}"
            )

            # Controles estrictos
            result = dict(totals)

            assert result.get(2019) == 39350
            assert result.get(2025) == 44838
            assert grand_total == 84188

        print(
            "\nDATA MART CARGADO "
            "Y VALIDADO CORRECTAMENTE ✓"
        )


if __name__ == "__main__":
    main()
