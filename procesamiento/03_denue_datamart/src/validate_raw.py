from pathlib import Path
from zipfile import ZipFile, BadZipFile
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Los ZIP originales del DENUE viven en la carpeta común del repositorio.
REPO_ROOT = PROJECT_ROOT.parents[1]
DENUE_DIR = REPO_ROOT / "datos" / "originales" / "03_inegi"

DATASETS = {
    2019: DENUE_DIR / "3.1_denue_2019_11",
    2025: DENUE_DIR / "3.2_denue_2025_05",
}

REQUIRED_COLUMNS = {
    "id",
    "nom_estab",
    "codigo_act",
    "nombre_act",
    "per_ocu",
    "entidad",
    "municipio",
    "localidad",
    "latitud",
    "longitud",
}


def find_denue_csv(zip_file: ZipFile):
    """Encuentra el CSV principal del DENUE dentro del ZIP."""
    candidates = [
        name for name in zip_file.namelist()
        if name.lower().endswith(".csv")
        and "conjunto_de_datos" in name.lower()
    ]

    if not candidates:
        raise ValueError("No se encontró el CSV principal de DENUE.")

    return candidates[0]


def validate_zip(zip_path: Path, year: int):
    """Valida estructura, columnas y coordenadas de un ZIP DENUE."""

    try:
        with ZipFile(zip_path) as z:
            csv_name = find_denue_csv(z)

            with z.open(csv_name) as csv_file:
                df = pd.read_csv(
                    csv_file,
                    encoding="latin-1",
                    low_memory=False
                )

    except BadZipFile:
        return {
            "year": year,
            "file": zip_path.name,
            "status": "ERROR: ZIP inválido",
        }

    except Exception as exc:
        return {
            "year": year,
            "file": zip_path.name,
            "status": f"ERROR: {exc}",
        }

    missing = REQUIRED_COLUMNS - set(df.columns)

    lat = pd.to_numeric(df["latitud"], errors="coerce")
    lon = pd.to_numeric(df["longitud"], errors="coerce")

    valid_coordinates = (
        lat.between(-90, 90)
        & lon.between(-180, 180)
    ).sum()

    return {
        "year": year,
        "file": zip_path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "valid_coordinates": int(valid_coordinates),
        "invalid_coordinates": int(len(df) - valid_coordinates),
        "missing_columns": ", ".join(sorted(missing)) if missing else "None",
        "status": "OK" if not missing else "WARNING",
    }


def main():
    results = []

    print("\n=== VALIDACIÓN RAW DENUE ===\n")

    for year, folder in DATASETS.items():

        zip_files = sorted(folder.glob("*.zip"))

        print(f"{year}: {len(zip_files)} ZIP encontrados")

        for zip_path in zip_files:
            result = validate_zip(zip_path, year)
            results.append(result)

            print(
                f"  {zip_path.name}: "
                f"{result.get('rows', 'N/A')} registros "
                f"[{result['status']}]"
            )

    report = pd.DataFrame(results)

    output_dir = PROJECT_ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "raw_validation_report.csv"
    report.to_csv(output_file, index=False)

    print("\n=== RESUMEN ===")

    if "rows" in report.columns:
        totals = report.groupby("year")["rows"].sum()

        for year, total in totals.items():
            print(f"{year}: {int(total):,} registros")

        print(f"TOTAL: {int(report['rows'].sum()):,} registros")

    print(f"\nReporte guardado en:\n{output_file}")


if __name__ == "__main__":
    main()
