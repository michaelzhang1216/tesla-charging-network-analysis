import gzip
import json
import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

EXTERNAL_DATA_DIR = BASE_DIR / "data" / "external" / "ocm-data"
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
DATABASE_DIR = BASE_DIR / "data" / "database"

POI_FILE = EXTERNAL_DATA_DIR / "poi.json.gz"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)


def load_ocm_poi_data(max_records: int | None = 5000) -> list[dict]:
    """
    Load OpenChargeMap POI data from local poi.json.gz file.

    The file contains one JSON object per line.
    """
    records = []

    with gzip.open(POI_FILE, "rt", encoding="utf-8") as file:
        for i, line in enumerate(file):
            if max_records is not None and i >= max_records:
                break

            line = line.strip()
            if not line:
                continue

            records.append(json.loads(line))

    return records

def safe_value(value):
    """
    Convert nested dict/list values into JSON strings for SQLite compatibility.
    """
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value

def flatten_charging_station_data(records: list[dict]) -> pd.DataFrame:
    """
    Convert nested OpenChargeMap records into a flat table.
    """
    rows = []

    for record in records:
        address = record.get("AddressInfo", {}) or {}
        operator = record.get("OperatorInfo", {}) or {}
        usage = record.get("UsageType", {}) or {}
        status = record.get("StatusType", {}) or {}
        connections = record.get("Connections", []) or []

        country_info = address.get("Country") or {}

        row = {
            "id": record.get("ID"),
            "uuid": record.get("UUID"),
            "station_title": address.get("Title"),
            "operator": operator.get("Title"),
            "usage_type": usage.get("Title"),
            "status": status.get("Title"),
            "country": country_info.get("Title") if isinstance(country_info, dict) else country_info,
            "iso_code": country_info.get("ISOCode") if isinstance(country_info, dict) else None,
            "state_or_province": address.get("StateOrProvince"),
            "town": address.get("Town"),
            "address_line_1": address.get("AddressLine1"),
            "postcode": address.get("Postcode"),
            "latitude": address.get("Latitude"),
            "longitude": address.get("Longitude"),
            "number_of_connections": len(connections),
            "date_created": record.get("DateCreated"),
            "date_last_verified": record.get("DateLastVerified"),
        }

        rows.append({key: safe_value(value) for key, value in row.items()})

    return pd.DataFrame(rows)


def save_to_csv(df: pd.DataFrame) -> Path:
    output_path = RAW_DATA_DIR / "openchargemap_charging_stations.csv"
    df.to_csv(output_path, index=False)
    return output_path


def save_to_sqlite(df: pd.DataFrame) -> Path:
    db_path = DATABASE_DIR / "tesla_charging_raw.db"

    with sqlite3.connect(db_path) as conn:
        df.to_sql(
            "openchargemap_charging_stations_sample",
            conn,
            if_exists="replace",
            index=False,
        )

    return db_path


def main() -> None:
    print("Loading OpenChargeMap POI data from local snapshot...")

    records = load_ocm_poi_data(max_records=None)

    print(f"Loaded {len(records)} records.")

    df = flatten_charging_station_data(records)

    csv_path = save_to_csv(df)
    db_path = save_to_sqlite(df)

    print(f"Saved CSV to: {csv_path}")
    print(f"Saved SQLite database to: {db_path}")

    print("\nPreview:")
    print(df.head())

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nMissing values:")
    print(df.isna().sum())


if __name__ == "__main__":
    main()