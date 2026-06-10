import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
EXTERNAL_DATA_DIR = BASE_DIR / "data" / "external"
DATABASE_DIR = BASE_DIR / "data" / "database"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "tesla_charging_raw.db"


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names for SQLite compatibility.
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )
    return df


def load_csv_to_sqlite(relative_path: str, table_name: str) -> None:
    """
    Load a CSV file from data/external into SQLite.
    """
    file_path = EXTERNAL_DATA_DIR / relative_path

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"\nLoading: {file_path}")

    df = pd.read_csv(file_path)
    df = clean_column_names(df)

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    print(f"Saved to SQLite table: {table_name}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Column names: {df.columns.tolist()}")


def main() -> None:
    load_csv_to_sqlite(
        relative_path="deliver2015-25/tesla_deliveries_dataset_2015_2025.csv",
        table_name="tesla_deliveries_2015_2025_raw",
    )

    load_csv_to_sqlite(
        relative_path="iea/EV Data Explorer 2026.csv",
        table_name="iea_ev_data_explorer_2026_raw",
    )

    load_csv_to_sqlite(
        relative_path="kaggle/global_ev_charging_station.csv",
        table_name="kaggle_global_ev_charging_station_raw",
    )

    load_csv_to_sqlite(
        relative_path="usgovenergy/alt_fuel_stations_historical_day (Jun 10 2026).csv",
        table_name="us_alt_fuel_stations_historical_raw",
    )


if __name__ == "__main__":
    main()