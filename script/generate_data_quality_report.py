import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "database" / "tesla_charging_raw.db"
REPORTS_DIR = BASE_DIR / "reports"
REPORT_PATH = REPORTS_DIR / "week1_data_quality_report.md"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


KEY_FIELDS = {
    "openchargemap_charging_stations_full": [
        "id",
        "station_title",
        "operator",
        "country",
        "latitude",
        "longitude",
        "number_of_connections",
    ],
    "tesla_deliveries_2015_2025_raw": [],
    "iea_ev_data_explorer_2026_raw": [],
    "kaggle_global_ev_charging_station_raw": [],
    "us_alt_fuel_stations_historical_raw": [
        "station_name",
        "city",
        "state",
        "latitude",
        "longitude",
        "ev_network",
        "ev_dc_fast_count",
    ],
    "world_bank_gdp_country_raw": [
        "country_name",
        "country_code",
        "indicator_name",
        "indicator_code",
    ],
    "world_bank_income_level_country_raw": [
        "country_code",
        "region",
        "incomegroup",
    ],
    "world_bank_population_raw": [
        "country_name",
        "country_code",
        "indicator_name",
        "indicator_code",
    ],
    "world_bank_road_density_raw": [],
}


def get_table_names(conn: sqlite3.Connection) -> list[str]:
    query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    tables = pd.read_sql(query, conn)
    return tables["name"].tolist()


def analyze_table(conn: sqlite3.Connection, table_name: str) -> dict:
    df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)

    row_count = len(df)
    column_count = len(df.columns)
    duplicate_count = int(df.duplicated().sum())

    missing_counts = df.isna().sum().sort_values(ascending=False)
    missing_rates = (df.isna().mean() * 100).sort_values(ascending=False)

    top_missing = pd.DataFrame(
        {
            "missing_count": missing_counts,
            "missing_rate_percent": missing_rates.round(2),
        }
    ).head(10)

    expected_fields = KEY_FIELDS.get(table_name, [])
    existing_fields = set(df.columns)
    missing_key_fields = [
        field for field in expected_fields if field not in existing_fields
    ]

    return {
        "table_name": table_name,
        "row_count": row_count,
        "column_count": column_count,
        "duplicate_count": duplicate_count,
        "columns": df.columns.tolist(),
        "top_missing": top_missing,
        "expected_fields": expected_fields,
        "missing_key_fields": missing_key_fields,
    }


def format_markdown_report(results: list[dict]) -> str:
    lines = []

    lines.append("# Week 1 Data Quality Assessment Report")
    lines.append("")
    lines.append("## 1. Overview")
    lines.append("")
    lines.append(
        "This report summarizes the initial data quality assessment for the raw datasets collected in Week 1. "
        "The assessment focuses on dataset size, field coverage, missing values, duplicate records, and key field availability."
    )
    lines.append("")

    lines.append("## 2. Database Summary")
    lines.append("")
    lines.append("| Table | Rows | Columns | Duplicate Rows |")
    lines.append("|---|---:|---:|---:|")

    for result in results:
        lines.append(
            f"| {result['table_name']} | {result['row_count']} | "
            f"{result['column_count']} | {result['duplicate_count']} |"
        )

    lines.append("")

    lines.append("## 3. Table-Level Quality Checks")
    lines.append("")

    for result in results:
        lines.append(f"### 3.x {result['table_name']}")
        lines.append("")
        lines.append(f"- Rows: {result['row_count']}")
        lines.append(f"- Columns: {result['column_count']}")
        lines.append(f"- Duplicate rows: {result['duplicate_count']}")
        lines.append("")

        lines.append("**Column names:**")
        lines.append("")
        lines.append(", ".join(result["columns"]))
        lines.append("")

        if result["expected_fields"]:
            lines.append("**Key field check:**")
            lines.append("")
            if result["missing_key_fields"]:
                lines.append(
                    f"- Missing key fields: {', '.join(result['missing_key_fields'])}"
                )
            else:
                lines.append("- All predefined key fields are present.")
            lines.append("")

        lines.append("**Top missing-value fields:**")
        lines.append("")
        lines.append("| Field | Missing Count | Missing Rate (%) |")
        lines.append("|---|---:|---:|")

        top_missing = result["top_missing"]
        for field, row in top_missing.iterrows():
            lines.append(
                f"| {field} | {int(row['missing_count'])} | "
                f"{row['missing_rate_percent']} |"
            )

        lines.append("")

    lines.append("## 4. Initial Findings")
    lines.append("")
    lines.append(
        "- Multiple raw data sources have been successfully collected and loaded into the SQLite database."
    )
    lines.append(
        "- Charging station datasets contain useful geographic fields such as latitude and longitude, which will support spatial analysis in later stages."
    )
    lines.append(
        "- Some datasets contain missing values in operator, usage type, status, or metadata fields. These fields should be reviewed during Week 2 data cleaning."
    )
    lines.append(
        "- World Bank datasets may have different structures depending on the indicator source. Some files may require reshaping from wide format to long country-year format."
    )
    lines.append(
        "- Dataset merging should not be performed in Week 1. Standardization, deduplication, and integration should be conducted in Week 2."
    )
    lines.append("")

    lines.append("## 5. Next Steps")
    lines.append("")
    lines.append(
        "- Standardize country names and country codes across charging station, EV sales, and external factor datasets."
    )
    lines.append(
        "- Convert World Bank yearly wide-format data into long format for country-year analysis."
    )
    lines.append(
        "- Identify Tesla-related charging stations from broader charging station datasets."
    )
    lines.append(
        "- Check duplicate stations using station name, operator, address, latitude, and longitude."
    )
    lines.append(
        "- Build a cleaned dataset for exploratory data analysis in Week 2."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        table_names = get_table_names(conn)
        print("Tables found:")
        for table_name in table_names:
            print(f"- {table_name}")

        results = []
        for table_name in table_names:
            print(f"\nAnalyzing table: {table_name}")
            results.append(analyze_table(conn, table_name))

    report = format_markdown_report(results)
    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"\nData quality report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()