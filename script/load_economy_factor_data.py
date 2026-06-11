import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
ECONOMY_DATA_DIR = BASE_DIR / "data" / "external" / "economy_factor_data"
DATABASE_DIR = BASE_DIR / "data" / "database"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "tesla_charging_raw.db"


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean column names for SQLite compatibility.
    """
    df = df.copy()

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace(".", "_", regex=False)
    )

    return df


def load_csv_to_sqlite(
    file_name: str,
    table_name: str,
    skiprows: int | None = None,
) -> None:
    """
    Load one economy factor CSV file into SQLite.
    """
    file_path = ECONOMY_DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"\nLoading: {file_path}")

    try:
        df = pd.read_csv(file_path, skiprows=skiprows)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, skiprows=skiprows, encoding="latin1")

    df = clean_column_names(df)

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    print(f"Saved to SQLite table: {table_name}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Column names: {df.columns.tolist()}")


def main() -> None:
    load_csv_to_sqlite(
        file_name="WB_GDP_Country.csv",
        table_name="world_bank_gdp_country_raw",
        skiprows=4,
    )

    load_csv_to_sqlite(
        file_name="WB_Incomelevel_Country.csv",
        table_name="world_bank_income_level_country_raw",
    )

    load_csv_to_sqlite(
        file_name="WB_Population.csv",
        table_name="world_bank_population_raw",
        skiprows=4,
    )

    load_csv_to_sqlite(
        file_name="WB_RoadDensity.csv",
        table_name="world_bank_road_density_raw",
        skiprows=4,
    )


if __name__ == "__main__":
    main()