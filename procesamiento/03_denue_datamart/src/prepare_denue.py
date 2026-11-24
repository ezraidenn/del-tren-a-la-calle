from pathlib import Path
from zipfile import ZipFile
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Los ZIP originales del DENUE viven en la carpeta común del repositorio.
REPO_ROOT = PROJECT_ROOT.parents[1]
DENUE_DIR = REPO_ROOT / "datos" / "originales" / "03_inegi"

DATASETS = {
    2019: DENUE_DIR / "3.1_denue_2019_11",
    2025: DENUE_DIR / "3.2_denue_2025_05",
}

KEEP_COLUMNS = [
    "id",
    "clee",
    "nom_estab",
    "codigo_act",
    "nombre_act",
    "per_ocu",
    "entidad",
    "municipio",
    "localidad",
    "nomb_asent",
    "cod_postal",
    "ageb",
    "latitud",
    "longitud",
    "fecha_alta",
]


def find_denue_csv(zip_file):
    candidates = [
        name for name in zip_file.namelist()
        if name.lower().endswith(".csv")
        and "conjunto_de_datos" in name.lower()
    ]

    if not candidates:
        raise ValueError("No se encontró el CSV principal.")

    return candidates[0]


def read_denue_zip(zip_path, year):
    with ZipFile(zip_path) as z:
        csv_name = find_denue_csv(z)

        with z.open(csv_name) as f:
            df = pd.read_csv(
                f,
                encoding="latin-1",
                low_memory=False
            )

    # Homogeneizar esquema
    for column in KEEP_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA

    df = df[KEEP_COLUMNS].copy()

    # Año del corte DENUE
    df["snapshot_year"] = year

    # Coordenadas numéricas
    df["latitud"] = pd.to_numeric(
        df["latitud"], errors="coerce"
    )

    df["longitud"] = pd.to_numeric(
        df["longitud"], errors="coerce"
    )

    return df


def process_year(year, folder):
    frames = []

    print(f"\nProcesando {year}...")

    for zip_path in sorted(folder.glob("*.zip")):
        df = read_denue_zip(zip_path, year)
        frames.append(df)

        print(
            f"  {zip_path.name}: "
            f"{len(df):,} registros"
        )

    result = pd.concat(
        frames,
        ignore_index=True
    )

    return result


def main():

    output_dir = PROJECT_ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    grand_total = 0

    for year, folder in DATASETS.items():

        df = process_year(year, folder)

        output_file = (
            output_dir /
            f"denue_{year}_normalized.parquet"
        )

        df.to_parquet(
            output_file,
            index=False
        )

        grand_total += len(df)

        print(
            f"\n{year}: {len(df):,} registros"
        )

        print(
            f"Archivo generado: {output_file}"
        )

        print(
            f"Coordenadas nulas: "
            f"{df[['latitud','longitud']].isna().any(axis=1).sum():,}"
        )

    print("\n=== PROCESAMIENTO COMPLETADO ===")
    print(f"Total procesado: {grand_total:,}")


if __name__ == "__main__":
    main()
