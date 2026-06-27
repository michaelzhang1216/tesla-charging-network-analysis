from pathlib import Path

import pandas as pd


PROCESSED_DIR = Path("data/processed")

INPUT_FILE = PROCESSED_DIR / "openchargemap_charging_stations_cleaned.csv"
BACKUP_FILE = PROCESSED_DIR / "openchargemap_charging_stations_cleaned_before_tesla_fix.csv"
OUTPUT_FILE = PROCESSED_DIR / "openchargemap_charging_stations_cleaned.csv"


def main() -> None:
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    # Save a backup before overwriting the cleaned table.
    df.to_csv(BACKUP_FILE, index=False)

    if "operator" not in df.columns:
        df["operator"] = pd.NA

    if "station_name" not in df.columns:
        raise ValueError("station_name column is missing from OCM cleaned table.")

    station_name_contains_tesla = (
        df["station_name"]
        .astype(str)
        .str.contains("tesla", case=False, na=False)
    )

    operator_contains_tesla = (
        df["operator"]
        .astype(str)
        .str.contains("tesla", case=False, na=False)
    )

    tesla_mask = station_name_contains_tesla | operator_contains_tesla

    before_count = (df["operator"].astype(str).str.lower() == "tesla").sum()

    df.loc[tesla_mask, "operator"] = "Tesla"

    after_count = (df["operator"].astype(str).str.lower() == "tesla").sum()

    df.to_csv(OUTPUT_FILE, index=False)

    print("OCM Tesla operator fix finished.")
    print(f"Input file: {INPUT_FILE}")
    print(f"Backup file: {BACKUP_FILE}")
    print(f"Output file overwritten: {OUTPUT_FILE}")
    print(f"Rows matched by station_name/operator containing Tesla: {tesla_mask.sum()}")
    print(f"Operator == Tesla before fix: {before_count}")
    print(f"Operator == Tesla after fix: {after_count}")


if __name__ == "__main__":
    main()
    