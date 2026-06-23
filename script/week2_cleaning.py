import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path("data/database/tesla_charging_raw.db")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names:
    lowercase, strip spaces, and replace common separators with underscores.
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
        .str.replace(":", "_", regex=False)
    )
    return df


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean text columns:
    strip spaces and convert empty-like strings to missing values.
    """
    df = df.copy()
    text_cols = df.select_dtypes(include=["object"]).columns

    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(
            {
                "": pd.NA,
                "None": pd.NA,
                "none": pd.NA,
                "nan": pd.NA,
                "NaN": pd.NA,
                "NULL": pd.NA,
                "null": pd.NA,
            }
        )

    return df


def clean_coordinate_columns(
    df: pd.DataFrame,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
) -> pd.DataFrame:
    """
    Keep latitude and longitude as original location fields,
    but only convert them to numeric.

    We do NOT create latitude/longitude-related features here.
    No has_valid_coordinates, lat_bin, lon_bin, or h3_index will be added.
    """
    df = df.copy()

    if lat_col in df.columns:
        df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")

    if lon_col in df.columns:
        df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")

    return df


def save_cleaned_table(
    df: pd.DataFrame,
    conn: sqlite3.Connection,
    table_name: str,
    csv_name: str,
) -> None:
    """
    Save cleaned data to both SQLite and CSV.
    """
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    df.to_csv(PROCESSED_DIR / csv_name, index=False)

    print(f"Saved: {table_name}")
    print(f"CSV: {PROCESSED_DIR / csv_name}")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    print("-" * 80)


def clean_openchargemap(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM openchargemap_charging_stations_sample", conn)

    df = clean_column_names(df)
    df = clean_text_columns(df)
    df = df.drop_duplicates()

    rename_map = {
        "station_title": "station_name",
        "state_or_province": "state",
        "town": "city",
        "address_line_1": "address",
        "number_of_connections": "connection_count",
        "date_created": "created_date",
        "date_last_verified": "last_verified_date",
    }
    df = df.rename(columns=rename_map)

    numeric_cols = [
        "id",
        "latitude",
        "longitude",
        "connection_count",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    date_cols = [
        "created_date",
        "last_verified_date",
    ]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df = clean_coordinate_columns(df)

    if "created_date" in df.columns:
        df["created_year"] = df["created_date"].dt.year
        df["created_month"] = df["created_date"].dt.month

    df["source"] = "openchargemap"

    return df


def clean_kaggle_charging(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM kaggle_global_ev_charging_station_raw", conn)

    df = clean_column_names(df)
    df = clean_text_columns(df)
    df = df.drop_duplicates()

    rename_map = {
        "stationid": "station_id",
        "dataproviderid": "data_provider_id",
        "usagetype": "usage_type",
        "usagecost": "usage_cost",
        "addresstitle": "station_name",
        "addressline1": "address",
        "stateorprovince": "state",
        "maxpowerkw": "max_power_kw",
        "fastchargecount": "fast_charge_count",
        "connectiontypes": "connection_types",
        "statustype": "status",
        "yearcreated": "created_year",
    }
    df = df.rename(columns=rename_map)

    numeric_cols = [
        "station_id",
        "data_provider_id",
        "latitude",
        "longitude",
        "max_power_kw",
        "fast_charge_count",
        "created_year",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = clean_coordinate_columns(df)

    if "created_year" in df.columns:
        df["created_year"] = df["created_year"].astype("Int64")

    df["source"] = "kaggle_global_ev_charging_station"

    return df


def clean_us_alt_fuel(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM us_alt_fuel_stations_historical_raw", conn)

    df = clean_column_names(df)
    df = clean_text_columns(df)
    df = df.drop_duplicates()

    # This raw table includes many fuel station types.
    # Keep only electric charging stations.
    if "fuel_type_code" in df.columns:
        df = df[df["fuel_type_code"].eq("ELEC")].copy()

    rename_map = {
        "street_address": "address",
        "zip": "postcode",
        "ev_network": "operator",
        "ev_dc_fast_count": "dc_fast_count",
        "ev_level1_evse_num": "level1_count",
        "ev_level2_evse_num": "level2_count",
        "date_last_confirmed": "last_confirmed_date",
    }
    df = df.rename(columns=rename_map)

    numeric_cols = [
        "id",
        "latitude",
        "longitude",
        "level1_count",
        "level2_count",
        "dc_fast_count",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    date_cols = [
        "open_date",
        "last_confirmed_date",
        "updated_at",
        "expected_date",
    ]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df = clean_coordinate_columns(df)

    count_cols = [
        col
        for col in ["level1_count", "level2_count", "dc_fast_count"]
        if col in df.columns
    ]

    if count_cols:
        df["ev_charger_count"] = df[count_cols].fillna(0).sum(axis=1)

    if "open_date" in df.columns:
        df["open_year"] = df["open_date"].dt.year
        df["open_month"] = df["open_date"].dt.month

    df["source"] = "us_alt_fuel_stations"

    return df


def clean_tesla_deliveries(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM tesla_deliveries_2015_2025_raw", conn)

    df = clean_column_names(df)
    df = clean_text_columns(df)
    df = df.drop_duplicates()

    numeric_cols = [
        "year",
        "month",
        "estimated_deliveries",
        "production_units",
        "avg_price_usd",
        "battery_capacity_kwh",
        "range_km",
        "co2_saved_tons",
        "charging_stations",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "year" in df.columns:
        df["year"] = df["year"].astype("Int64")

    if "month" in df.columns:
        df["month"] = df["month"].astype("Int64")

    if {"year", "month"}.issubset(df.columns):
        df["date"] = pd.to_datetime(
            df["year"].astype(str) + "-" + df["month"].astype(str) + "-01",
            errors="coerce",
        )
        df["quarter"] = df["date"].dt.quarter

    df["source"] = "tesla_deliveries"

    return df


def clean_iea_ev_data(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM iea_ev_data_explorer_2026_raw", conn)

    df = clean_column_names(df)
    df = clean_text_columns(df)
    df = df.drop_duplicates()

    rename_map = {
        "region_country": "country_or_region",
    }
    df = df.rename(columns=rename_map)

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    required_cols = [
        col
        for col in ["country_or_region", "year", "value"]
        if col in df.columns
    ]

    if required_cols:
        df = df.dropna(subset=required_cols)

    df["source"] = "iea_ev_data_explorer"

    return df


def clean_world_bank_gdp(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM world_bank_gdp_country_raw", conn)

    df = clean_column_names(df)
    df = clean_text_columns(df)
    df = df.drop_duplicates()

    # Remove unnamed columns.
    df = df.loc[:, ~df.columns.str.startswith("unnamed")]

    id_cols = [
        "country_name",
        "country_code",
        "indicator_name",
        "indicator_code",
    ]

    year_cols = [col for col in df.columns if col.isdigit()]

    df_long = df.melt(
        id_vars=id_cols,
        value_vars=year_cols,
        var_name="year",
        value_name="gdp",
    )

    df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce").astype("Int64")
    df_long["gdp"] = pd.to_numeric(df_long["gdp"], errors="coerce")

    df_long = df_long.dropna(
        subset=[
            "country_code",
            "country_name",
            "year",
            "gdp",
        ]
    )

    df_long = df_long.drop_duplicates()
    df_long["source"] = "world_bank_gdp"

    return df_long


def clean_world_bank_income(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM world_bank_income_level_country_raw", conn)

    df = clean_column_names(df)
    df = clean_text_columns(df)
    df = df.drop_duplicates()

    df = df.loc[:, ~df.columns.str.startswith("unnamed")]

    rename_map = {
        "incomegroup": "income_group",
        "tablename": "country_name",
        "specialnotes": "special_notes",
    }
    df = df.rename(columns=rename_map)

    keep_cols = [
        col
        for col in [
            "country_code",
            "country_name",
            "region",
            "income_group",
            "special_notes",
        ]
        if col in df.columns
    ]

    df = df[keep_cols].copy()
    df = df.dropna(subset=["country_code"])

    df["source"] = "world_bank_income_level"

    return df


def clean_population_from_original_csv() -> pd.DataFrame:
    """
    Clean World Bank Population Data360 CSV.

    The raw table in SQLite has wrong headers, so this function reads
    the original CSV directly.
    """
    file_path = Path("data/external/economy_factor_data/WB_Population.csv")

    df = pd.read_csv(file_path)
    df = clean_column_names(df)
    df = clean_text_columns(df)

    keep_cols = [
        "ref_area",
        "ref_area_label",
        "indicator",
        "indicator_label",
        "time_period",
        "obs_value",
        "unit_measure",
        "unit_measure_label",
    ]

    df = df[keep_cols].copy()

    df = df.rename(
        columns={
            "ref_area": "country_code",
            "ref_area_label": "country_name",
            "indicator": "indicator_code",
            "indicator_label": "indicator_name",
            "time_period": "year",
            "obs_value": "population",
            "unit_measure": "unit_code",
            "unit_measure_label": "unit_label",
        }
    )

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")

    df = df.dropna(
        subset=[
            "country_code",
            "country_name",
            "year",
            "population",
        ]
    )

    df = df.drop_duplicates()
    df["source"] = "world_bank_population"

    return df


def clean_road_density_from_original_csv() -> pd.DataFrame:
    """
    Clean World Bank Road Density Data360 CSV.

    The raw table in SQLite has wrong headers, so this function reads
    the original CSV directly.

    Road density includes value, score, and rank records.
    We only keep actual value records.
    """
    file_path = Path("data/external/economy_factor_data/WB_RoadDensity.csv")

    df = pd.read_csv(file_path)
    df = clean_column_names(df)
    df = clean_text_columns(df)

    # Keep only real numeric road density value.
    # Do not keep score or rank.
    if "comp_breakdown_1" in df.columns:
        df = df[df["comp_breakdown_1"].eq("WEF_TTDI_VAL")].copy()

    keep_cols = [
        "ref_area",
        "ref_area_label",
        "indicator",
        "indicator_label",
        "time_period",
        "obs_value",
        "unit_measure",
        "unit_measure_label",
    ]

    df = df[keep_cols].copy()

    df = df.rename(
        columns={
            "ref_area": "country_code",
            "ref_area_label": "country_name",
            "indicator": "indicator_code",
            "indicator_label": "indicator_name",
            "time_period": "year",
            "obs_value": "road_density",
            "unit_measure": "unit_code",
            "unit_measure_label": "unit_label",
        }
    )

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["road_density"] = pd.to_numeric(df["road_density"], errors="coerce")

    df = df.dropna(
        subset=[
            "country_code",
            "country_name",
            "year",
            "road_density",
        ]
    )

    df = df.drop_duplicates()
    df["source"] = "world_bank_road_density"

    return df


def main() -> None:
    conn = sqlite3.connect(DB_PATH)

    cleaned_tables = {
        "openchargemap_charging_stations_cleaned": (
            clean_openchargemap(conn),
            "openchargemap_charging_stations_cleaned.csv",
        ),
        "kaggle_global_ev_charging_station_cleaned": (
            clean_kaggle_charging(conn),
            "kaggle_global_ev_charging_station_cleaned.csv",
        ),
        "us_alt_fuel_stations_historical_cleaned": (
            clean_us_alt_fuel(conn),
            "us_alt_fuel_stations_historical_cleaned.csv",
        ),
        "tesla_deliveries_2015_2025_cleaned": (
            clean_tesla_deliveries(conn),
            "tesla_deliveries_2015_2025_cleaned.csv",
        ),
        "iea_ev_data_explorer_2026_cleaned": (
            clean_iea_ev_data(conn),
            "iea_ev_data_explorer_2026_cleaned.csv",
        ),
        "world_bank_gdp_country_cleaned": (
            clean_world_bank_gdp(conn),
            "world_bank_gdp_country_cleaned.csv",
        ),
        "world_bank_income_level_country_cleaned": (
            clean_world_bank_income(conn),
            "world_bank_income_level_country_cleaned.csv",
        ),
        "world_bank_population_cleaned": (
            clean_population_from_original_csv(),
            "world_bank_population_cleaned.csv",
        ),
        "world_bank_road_density_cleaned": (
            clean_road_density_from_original_csv(),
            "world_bank_road_density_cleaned.csv",
        ),
    }

    for table_name, (df, csv_name) in cleaned_tables.items():
        save_cleaned_table(
            df=df,
            conn=conn,
            table_name=table_name,
            csv_name=csv_name,
        )

    conn.close()

    print()
    print("Week 2 cleaning completed.")
    print("Cleaned CSV files are saved in data/processed/.")
    print("Cleaned SQLite tables are saved in data/database/tesla_charging_raw.db.")


if __name__ == "__main__":
    main()