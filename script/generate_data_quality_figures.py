import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "database" / "tesla_charging_raw.db"

REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
REPORT_PATH = REPORTS_DIR / "week1_data_quality_report.md"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


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
    "openchargemap_charging_stations_sample": [
        "id",
        "station_title",
        "operator",
        "country",
        "latitude",
        "longitude",
        "number_of_connections",
    ],
    "tesla_deliveries_2015_2025_raw": [
        "year",
        "month",
        "region",
        "model",
        "estimated_deliveries",
    ],
    "iea_ev_data_explorer_2026_raw": [
        "region_country",
        "category",
        "parameter",
        "year",
        "value",
    ],
    "kaggle_global_ev_charging_station_raw": [
        "stationid",
        "operator",
        "country",
        "latitude",
        "longitude",
    ],
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


def create_summary_dataframe(results: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "table_name": result["table_name"],
                "row_count": result["row_count"],
                "column_count": result["column_count"],
                "duplicate_count": result["duplicate_count"],
            }
            for result in results
        ]
    )


def plot_row_counts(summary_df: pd.DataFrame) -> None:
    plot_df = summary_df.sort_values("row_count", ascending=False)

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["table_name"], plot_df["row_count"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Row Count")
    plt.title("Row Counts by Raw Data Table")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "table_row_counts.png", dpi=300)
    plt.close()


def plot_duplicate_counts(summary_df: pd.DataFrame) -> None:
    plot_df = summary_df.sort_values("duplicate_count", ascending=False)

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["table_name"], plot_df["duplicate_count"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Duplicate Row Count")
    plt.title("Duplicate Rows by Raw Data Table")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "table_duplicate_counts.png", dpi=300)
    plt.close()


def plot_column_counts(summary_df: pd.DataFrame) -> None:
    plot_df = summary_df.sort_values("column_count", ascending=False)

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["table_name"], plot_df["column_count"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Column Count")
    plt.title("Column Counts by Raw Data Table")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "table_column_counts.png", dpi=300)
    plt.close()


def plot_top_missing_fields(
    result: dict,
    output_file: str,
    top_n: int = 10,
) -> None:
    top_missing = result["top_missing"].copy()

    if top_missing.empty:
        return

    top_missing = top_missing.sort_values("missing_rate_percent", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top_missing.index, top_missing["missing_rate_percent"])
    plt.xlabel("Missing Rate (%)")
    plt.title(f"Top Missing Fields: {result['table_name']}")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / output_file, dpi=300)
    plt.close()


def generate_figures(results: list[dict]) -> list[dict]:
    summary_df = create_summary_dataframe(results)

    plot_row_counts(summary_df)
    plot_duplicate_counts(summary_df)
    plot_column_counts(summary_df)

    figure_info = [
        {
            "title": "Figure 1. Row Counts by Raw Data Table",
            "path": "figures/table_row_counts.png",
            "description": (
                "This figure compares the number of records across all raw tables. "
                "It helps identify which data sources contribute the largest amount of data."
            ),
        },
        {
            "title": "Figure 2. Duplicate Rows by Raw Data Table",
            "path": "figures/table_duplicate_counts.png",
            "description": (
                "This figure shows the number of fully duplicated rows in each raw table. "
                "Tables with duplicate rows will need further review during Week 2 cleaning."
            ),
        },
        {
            "title": "Figure 3. Column Counts by Raw Data Table",
            "path": "figures/table_column_counts.png",
            "description": (
                "This figure compares the number of fields available in each raw table. "
                "Tables with more columns may require more careful field selection and standardization."
            ),
        },
    ]

    missing_plot_targets = {
        "openchargemap_charging_stations_sample": "ocm_top_missing.png",
        "openchargemap_charging_stations_full": "ocm_top_missing.png",
        "kaggle_global_ev_charging_station_raw": "kaggle_top_missing.png",
        "us_alt_fuel_stations_historical_raw": "us_alt_fuel_top_missing.png",
        "iea_ev_data_explorer_2026_raw": "iea_top_missing.png",
        "world_bank_gdp_country_raw": "world_bank_gdp_top_missing.png",
        "world_bank_income_level_country_raw": "world_bank_income_top_missing.png",
    }

    for result in results:
        table_name = result["table_name"]
        if table_name in missing_plot_targets:
            output_file = missing_plot_targets[table_name]
            plot_top_missing_fields(result, output_file)

            figure_info.append(
                {
                    "title": f"Missing Values: {table_name}",
                    "path": f"figures/{output_file}",
                    "description": (
                        "This figure shows the top fields with the highest missing-value rates "
                        f"in `{table_name}`."
                    ),
                }
            )

    return figure_info


def format_markdown_report(results: list[dict], figure_info: list[dict]) -> str:
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

    lines.append("## 3. Visual Summary")
    lines.append("")
    lines.append(
        "The following figures provide a quick visual summary of dataset size, duplication, field coverage, and missing-value patterns."
    )
    lines.append("")

    for figure in figure_info:
        lines.append(f"### {figure['title']}")
        lines.append("")
        lines.append(figure["description"])
        lines.append("")
        lines.append(f"![{figure['title']}]({figure['path']})")
        lines.append("")

    lines.append("## 4. Table-Level Quality Checks")
    lines.append("")

    for idx, result in enumerate(results, start=1):
        lines.append(f"### 4.{idx} {result['table_name']}")
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

    lines.append("## 5. Initial Findings")
    lines.append("")
    lines.append(
        "- Multiple raw data sources have been successfully collected and loaded into the SQLite database."
    )
    lines.append(
        "- Charging station datasets contain useful geographic fields such as latitude and longitude, which will support spatial analysis in later stages."
    )
    lines.append(
        "- Some datasets contain missing values in operator, usage type, status, pricing, or metadata fields. These fields should be reviewed during Week 2 data cleaning."
    )
    lines.append(
        "- Some World Bank datasets have different structures depending on the indicator source. These files may require reshaping into a consistent country-year format."
    )
    lines.append(
        "- A small number of duplicate rows exist in selected raw tables. Duplicate station checks should use station name, operator, address, latitude, and longitude instead of exact-row matching only."
    )
    lines.append(
        "- Dataset merging should not be performed before standardization. Standardization, deduplication, and integration should be conducted in Week 2."
    )
    lines.append("")

    lines.append("## 6. Next Steps")
    lines.append("")
    lines.append(
        "- Standardize country names and country codes across charging station, EV sales, and external factor datasets."
    )
    lines.append(
        "- Convert World Bank data into a more consistent country-year format when needed."
    )
    lines.append(
        "- Identify Tesla-related charging stations from broader charging station datasets."
    )
    lines.append(
        "- Check duplicate charging stations using station name, operator, address, latitude, and longitude."
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

    print("\nGenerating figures...")
    figure_info = generate_figures(results)

    print("Generating markdown report...")
    report = format_markdown_report(results, figure_info)
    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"\nData quality report saved to: {REPORT_PATH}")
    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()