from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/week3")
FIGURE_DIR = OUTPUT_DIR / "figures"

ANALYSIS_YEAR = 2025

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


COUNTRY_NAME_MAPPING = {
    # United States
    "united states of america": "united states",
    "usa": "united states",
    "u.s.": "united states",
    "u.s.a.": "united states",

    # United Kingdom
    "uk": "united kingdom",
    "great britain": "united kingdom",

    # Turkey
    "turkiye": "turkey",
    "türkiye": "turkey",

    # Czech Republic / Czechia
    # Population file may use Czechia, while charging data uses Czech Republic.
    "czech republic": "czechia",

    # Korea
    "korea; republic of": "south korea",
    "korea, republic of": "south korea",
    "korea, rep.": "south korea",
    "republic of korea": "south korea",

    # Taiwan
    "taiwan; province of china": "taiwan",
    "taiwan, province of china": "taiwan",
    "taiwan province of china": "taiwan",

    # China / Hong Kong / Macao
    "china mainland": "china",
    "hong kong sar": "hong kong",
    "hong kong sar, china": "hong kong",
    "macao sar": "macao",
    "macao sar, china": "macao",
    "macau": "macao",

    # Iran
    "iran; islamic republic of": "iran",
    "iran, islamic republic of": "iran",
    "iran, islamic rep.": "iran",

    # Moldova
    "moldova; republic of": "moldova",
    "moldova, republic of": "moldova",

    # Macedonia
    "macedonia": "north macedonia",
    "macedonia, fyr": "north macedonia",
    "north macedonia": "north macedonia",

    # Russia
    "russian federation": "russia",

    # Vietnam
    "viet nam": "vietnam",

    # Slovakia
    "slovak republic": "slovakia",

    # Egypt
    "egypt, arab rep.": "egypt",

    # Venezuela
    "venezuela, rb": "venezuela",

    # Congo variants
    "dr congo": "democratic republic of the congo",
    "drc": "democratic republic of the congo",
    "congo, dem. rep.": "democratic republic of the congo",
    "congo, democratic republic of the": "democratic republic of the congo",

    # Côte d'Ivoire
    "cote d'ivoire": "ivory coast",
    "côte d'ivoire": "ivory coast",

    # Swaziland changed name
    "swaziland": "eswatini",

    # Palestine
    "palestinian territory; occupied": "palestine",
    "palestinian territory, occupied": "palestine",
    "west bank and gaza": "palestine",
}


def clean_country_name(series: pd.Series) -> pd.Series:
    """Standardize country names for basic cross-table matching."""
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.lower()
    )

    return cleaned.replace(COUNTRY_NAME_MAPPING)


def load_data() -> dict[str, pd.DataFrame]:
    """Load cleaned datasets from data/processed."""
    data = {
        "kaggle": pd.read_csv(
            PROCESSED_DIR / "kaggle_global_ev_charging_station_cleaned.csv",
            low_memory=False,
        ),
        "ocm": pd.read_csv(
            PROCESSED_DIR / "openchargemap_charging_stations_cleaned.csv",
            low_memory=False,
        ),
        "iea": pd.read_csv(
            PROCESSED_DIR / "iea_ev_data_explorer_2026_cleaned.csv",
            low_memory=False,
        ),
        "gdp": pd.read_csv(
            PROCESSED_DIR / "world_gdp_bycountry_2025_cleaned.csv",
            low_memory=False,
        ),
        "population": pd.read_csv(
            PROCESSED_DIR / "world_population_bycountry_2025_cleaned.csv",
            low_memory=False,
        ),
        "income": pd.read_csv(
            PROCESSED_DIR / "world_bank_income_level_country_cleaned.csv",
            low_memory=False,
        ),
        "road": pd.read_csv(
            PROCESSED_DIR / "world_bank_road_density_cleaned.csv",
            low_memory=False,
        ),
    }

    return data


def build_charging_station_master(
    kaggle: pd.DataFrame,
    ocm: pd.DataFrame,
) -> pd.DataFrame:
    """Create a combined charging station table for Week 3 EDA."""

    kaggle_cols = [
        "station_id",
        "station_name",
        "operator",
        "country",
        "state",
        "town",
        "address",
        "latitude",
        "longitude",
        "max_power_kw",
        "fast_charge_count",
        "created_year",
        "source",
    ]

    ocm_cols = [
        "id",
        "station_name",
        "operator",
        "country",
        "iso_code",
        "state",
        "city",
        "address",
        "latitude",
        "longitude",
        "connection_count",
        "created_year",
        "source",
    ]

    kaggle_sub = kaggle[[col for col in kaggle_cols if col in kaggle.columns]].copy()
    ocm_sub = ocm[[col for col in ocm_cols if col in ocm.columns]].copy()

    kaggle_sub = kaggle_sub.rename(
        columns={
            "station_id": "source_station_id",
            "town": "city",
        }
    )

    ocm_sub = ocm_sub.rename(
        columns={
            "id": "source_station_id",
            "iso_code": "country_code",
        }
    )

    if "country_code" not in kaggle_sub.columns:
        kaggle_sub["country_code"] = pd.NA

    if "max_power_kw" not in ocm_sub.columns:
        ocm_sub["max_power_kw"] = pd.NA

    if "fast_charge_count" not in ocm_sub.columns:
        ocm_sub["fast_charge_count"] = pd.NA

    if "connection_count" not in kaggle_sub.columns:
        kaggle_sub["connection_count"] = pd.NA

    common_cols = [
        "source_station_id",
        "station_name",
        "operator",
        "country",
        "country_code",
        "state",
        "city",
        "address",
        "latitude",
        "longitude",
        "max_power_kw",
        "fast_charge_count",
        "connection_count",
        "created_year",
        "source",
    ]

    charging = pd.concat(
        [kaggle_sub[common_cols], ocm_sub[common_cols]],
        ignore_index=True,
    )

    charging["latitude"] = pd.to_numeric(charging["latitude"], errors="coerce")
    charging["longitude"] = pd.to_numeric(charging["longitude"], errors="coerce")
    charging["max_power_kw"] = pd.to_numeric(charging["max_power_kw"], errors="coerce")
    charging["fast_charge_count"] = pd.to_numeric(
        charging["fast_charge_count"],
        errors="coerce",
    )
    charging["connection_count"] = pd.to_numeric(
        charging["connection_count"],
        errors="coerce",
    )

    charging = charging.dropna(subset=["country", "latitude", "longitude"])
    charging = charging[
        charging["latitude"].between(-90, 90)
        & charging["longitude"].between(-180, 180)
    ]

    charging["country_key"] = clean_country_name(charging["country"])

    return charging


def get_2025_gdp(gdp: pd.DataFrame) -> pd.DataFrame:
    """
    Use the new cleaned 2025 GDP dataset.

    Expected columns:
    country_key, country_name, year, gdp_billion_usd, gdp
    """
    gdp = gdp.copy()

    # Safety check: if country_key is missing, recreate it from country_name.
    if "country_key" not in gdp.columns:
        if "country_name" not in gdp.columns:
            raise ValueError(
                "GDP table must contain either country_key or country_name."
            )
        gdp["country_key"] = clean_country_name(gdp["country_name"])

    gdp["year"] = pd.to_numeric(gdp["year"], errors="coerce")
    gdp["gdp"] = pd.to_numeric(gdp["gdp"], errors="coerce")

    gdp_2025 = gdp[gdp["year"] == ANALYSIS_YEAR].copy()

    return gdp_2025[
        [
            "country_key",
            "country_name",
            "year",
            "gdp",
        ]
    ].rename(
        columns={
            "year": "gdp_year",
            "country_name": "gdp_country_name",
        }
    )

def get_2025_population(population: pd.DataFrame) -> pd.DataFrame:
    """
    Use the new cleaned 2025 population dataset.

    Expected columns:
    country_key, country_name, year, population
    """
    population = population.copy()

    # Safety check: if country_key is missing, recreate it from country_name.
    if "country_key" not in population.columns:
        if "country_name" not in population.columns:
            raise ValueError(
                "Population table must contain either country_key or country_name."
            )
        population["country_key"] = clean_country_name(population["country_name"])

    population["year"] = pd.to_numeric(population["year"], errors="coerce")
    population["population"] = pd.to_numeric(
        population["population"],
        errors="coerce",
    )

    population_2025 = population[population["year"] == ANALYSIS_YEAR].copy()

    return population_2025[
        [
            "country_key",
            "country_name",
            "year",
            "population",
        ]
    ].rename(
        columns={
            "year": "population_year",
            "country_name": "population_country_name",
        }
    )

def get_income_group(income: pd.DataFrame) -> pd.DataFrame:
    income = income.copy()
    income["country_key"] = clean_country_name(income["country_name"])

    return income[
        ["country_key", "region", "income_group"]
    ].drop_duplicates("country_key")


def get_2025_road_density(road: pd.DataFrame) -> pd.DataFrame:
    road = road.copy()
    road["year"] = pd.to_numeric(road["year"], errors="coerce")
    road["road_density"] = pd.to_numeric(road["road_density"], errors="coerce")
    road["country_key"] = clean_country_name(road["country_name"])

    road_2025 = road[road["year"] == ANALYSIS_YEAR].copy()

    return road_2025[
        ["country_key", "year", "road_density"]
    ].rename(columns={"year": "road_density_year"})


def get_2025_iea_country_features(iea: pd.DataFrame) -> pd.DataFrame:
    """
    Build 2025 IEA country-level features.

    Important:
    IEA has multiple rows per country-year-parameter because values are split by
    mode and powertrain. For EV stock and EV sales, this function sums value
    across mode and powertrain within the same country and year.
    """
    iea = iea.copy()

    iea["year"] = pd.to_numeric(iea["year"], errors="coerce")
    iea["value"] = pd.to_numeric(iea["value"], errors="coerce")
    iea["country_key"] = clean_country_name(iea["country_or_region"])
    iea["parameter_key"] = clean_country_name(iea["parameter"])

    iea_2025 = iea[iea["year"] == ANALYSIS_YEAR].copy()

    iea_2025 = iea_2025[
        iea_2025["parameter_key"].isin(
            [
                "ev stock",
                "ev sales",
                "ev charging points",
            ]
        )
    ].copy()

    iea_country_parameter = (
        iea_2025.groupby(["country_key", "parameter_key"], as_index=False)
        .agg(
            iea_year=("year", "max"),
            value=("value", "sum"),
        )
    )

    iea_wide = iea_country_parameter.pivot_table(
        index="country_key",
        columns="parameter_key",
        values="value",
        aggfunc="sum",
    ).reset_index()

    iea_wide = iea_wide.rename(
        columns={
            "ev stock": "ev_stock",
            "ev sales": "ev_sales",
            "ev charging points": "iea_ev_charging_points",
        }
    )

    return iea_wide


def build_country_level_table(
    charging: pd.DataFrame,
    gdp: pd.DataFrame,
    population: pd.DataFrame,
    income: pd.DataFrame,
    road: pd.DataFrame,
    iea: pd.DataFrame,
) -> pd.DataFrame:
    """Build country-level analysis table for Week 3."""

    country_charging = (
        charging.groupby("country_key")
        .agg(
            country=("country", "first"),
            station_count=("source_station_id", "count"),
            tesla_station_record_count=(
                "operator",
                lambda x: x.astype(str).str.lower().eq("tesla").sum(),
            ),
            avg_max_power_kw=("max_power_kw", "mean"),
            total_fast_charge_count=("fast_charge_count", "sum"),
            total_connection_count=("connection_count", "sum"),
        )
        .reset_index()
    )

    gdp_2025 = get_2025_gdp(gdp)
    population_2025 = get_2025_population(population)
    income_sub = get_income_group(income)
    road_2025 = get_2025_road_density(road)
    iea_2025 = get_2025_iea_country_features(iea)

    country_level = country_charging.merge(gdp_2025, on="country_key", how="left")
    country_level = country_level.merge(population_2025, on="country_key", how="left")
    country_level = country_level.merge(income_sub, on="country_key", how="left")
    country_level = country_level.merge(road_2025, on="country_key", how="left")
    country_level = country_level.merge(iea_2025, on="country_key", how="left")

    country_level["gdp_per_capita"] = (
        country_level["gdp"] / country_level["population"]
    )

    country_level["stations_per_million_people"] = (
        country_level["station_count"] / country_level["population"] * 1_000_000
    )

    country_level["stations_per_billion_gdp"] = (
        country_level["station_count"] / (country_level["gdp"] / 1_000_000_000)
    )

    country_level["stations_per_100k_ev_stock"] = (
        country_level["station_count"] / country_level["ev_stock"] * 100_000
    )
    country_level["charging_point_proxy"] = (
        country_level["total_connection_count"].fillna(0)
        + country_level["total_fast_charge_count"].fillna(0)
    )

    country_level.loc[
        country_level["charging_point_proxy"] == 0,
        "charging_point_proxy",
    ] = pd.NA

    country_level["charging_points_per_million_people_proxy"] = (
        country_level["charging_point_proxy"]
        / country_level["population"]
        * 1_000_000
    )

    country_level["charging_points_per_100k_ev_stock_proxy"] = (
        country_level["charging_point_proxy"]
        / country_level["ev_stock"]
        * 100_000
    )
    country_level["tesla_station_share"] = (
        country_level["tesla_station_record_count"] / country_level["station_count"]
    )

    return country_level


def save_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    output_path: Path,
    top_n: int = 20,
) -> None:
    plot_df = (
        df.dropna(subset=[x_col, y_col])
        .sort_values(x_col, ascending=False)
        .head(top_n)
    )

    plt.figure(figsize=(10, 7))
    plt.barh(plot_df[y_col], plot_df[x_col])
    plt.gca().invert_yaxis()
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def save_scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    output_path: Path,
) -> None:
    plot_df = df.dropna(subset=[x_col, y_col]).copy()

    plt.figure(figsize=(8, 6))
    plt.scatter(plot_df[x_col], plot_df[y_col], alpha=0.6)
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def save_global_scatter_map(charging: pd.DataFrame) -> None:
    sample = charging.sample(
        n=min(50000, len(charging)),
        random_state=42,
    )

    plt.figure(figsize=(13, 7))
    plt.scatter(sample["longitude"], sample["latitude"], s=2, alpha=0.3)
    plt.title("Global EV Charging Station Spatial Distribution")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "global_charging_station_scatter.png", dpi=300)
    plt.close()


def save_correlation_heatmap(country_level: pd.DataFrame) -> pd.DataFrame:
    corr_cols = [
        "station_count",
        "tesla_station_record_count",
        "tesla_station_share",
        "avg_max_power_kw",
        "total_fast_charge_count",
        "total_connection_count",
        "population",
        "gdp",
        "gdp_per_capita",
        "road_density",
        "ev_stock",
        "ev_sales",
        "iea_ev_charging_points",
        "stations_per_million_people",
        "stations_per_billion_gdp",
        "stations_per_100k_ev_stock",
    ]

    available_cols = [col for col in corr_cols if col in country_level.columns]
    corr = country_level[available_cols].corr(numeric_only=True)

    plt.figure(figsize=(13, 10))
    plt.imshow(corr, aspect="auto")
    plt.colorbar(label="Correlation")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title("Week 3 Correlation Matrix Based on 2025 Country-Level Features")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "correlation_heatmap.png", dpi=300)
    plt.close()

    corr.to_csv(OUTPUT_DIR / "week3_correlation_matrix.csv", index=True)

    return corr


def print_missing_summary(country_level: pd.DataFrame) -> None:
    important_cols = [
        "population",
        "gdp",
        "road_density",
        "ev_stock",
        "ev_sales",
        "iea_ev_charging_points",
    ]

    print()
    print("Missing value summary for 2025 country-level features:")
    for col in important_cols:
        if col in country_level.columns:
            missing_count = country_level[col].isna().sum()
            print(f"{col}: {missing_count} missing out of {len(country_level)} countries")

def print_missing_countries(country_level: pd.DataFrame) -> None:
    check_cols = ["population", "gdp", "ev_stock", "ev_sales"]

    for col in check_cols:
        if col not in country_level.columns:
            continue

        missing_df = country_level[country_level[col].isna()].copy()

        print()
        print("=" * 80)
        print(f"Countries missing {col}: {len(missing_df)}")
        print(
            missing_df[
                [
                    "country",
                    "country_key",
                    "station_count",
                ]
            ]
            .sort_values("station_count", ascending=False)
            .head(30)
        )

def save_log_scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    output_path: Path,
) -> None:
    plot_df = df.dropna(subset=[x_col, y_col]).copy()
    plot_df = plot_df[(plot_df[x_col] > 0) & (plot_df[y_col] > 0)]

    plt.figure(figsize=(8, 6))
    plt.scatter(plot_df[x_col], plot_df[y_col], alpha=0.6)
    plt.xscale("log")
    plt.yscale("log")
    plt.title(title)
    plt.xlabel(f"{x_col} (log scale)")
    plt.ylabel(f"{y_col} (log scale)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def main() -> None:
    data = load_data()

    charging = build_charging_station_master(
        kaggle=data["kaggle"],
        ocm=data["ocm"],
    )

    charging.to_csv(
        PROCESSED_DIR / "week3_charging_station_master.csv",
        index=False,
    )

    country_level = build_country_level_table(
        charging=charging,
        gdp=data["gdp"],
        population=data["population"],
        income=data["income"],
        road=data["road"],
        iea=data["iea"],
    )

    country_level.to_csv(
        PROCESSED_DIR / "week3_country_level_analysis.csv",
        index=False,
    )

    save_global_scatter_map(charging)

    save_bar_chart(
        country_level,
        x_col="station_count",
        y_col="country",
        title="Top 20 Countries by Charging Station Count",
        output_path=FIGURE_DIR / "top20_countries_by_station_count.png",
    )

    save_bar_chart(
        country_level,
        x_col="stations_per_million_people",
        y_col="country",
        title="Top 20 Countries by Charging Stations per Million People",
        output_path=FIGURE_DIR / "top20_countries_by_stations_per_million_people.png",
    )

    save_bar_chart(
        country_level,
        x_col="tesla_station_record_count",
        y_col="country",
        title="Top 20 Countries by Tesla Charging Station Records",
        output_path=FIGURE_DIR / "top20_countries_by_tesla_station_records.png",
    )

    save_scatter_plot(
        country_level,
        x_col="gdp",
        y_col="station_count",
        title="2025 GDP vs Charging Station Count",
        output_path=FIGURE_DIR / "gdp_vs_station_count.png",
    )

    save_scatter_plot(
        country_level,
        x_col="population",
        y_col="station_count",
        title="2025 Population vs Charging Station Count",
        output_path=FIGURE_DIR / "population_vs_station_count.png",
    )

    save_scatter_plot(
        country_level,
        x_col="ev_stock",
        y_col="station_count",
        title="2025 EV Stock vs Charging Station Count",
        output_path=FIGURE_DIR / "ev_stock_vs_station_count.png",
    )

    save_scatter_plot(
        country_level,
        x_col="ev_sales",
        y_col="station_count",
        title="2025 EV Sales vs Charging Station Count",
        output_path=FIGURE_DIR / "ev_sales_vs_station_count.png",
    )

    corr = save_correlation_heatmap(country_level)
    save_log_scatter_plot(
        country_level,
        x_col="gdp",
        y_col="station_count",
        title="2025 GDP vs Charging Station Count Log Scale",
        output_path=FIGURE_DIR / "gdp_vs_station_count_log.png",
    )

    save_log_scatter_plot(
        country_level,
        x_col="population",
        y_col="station_count",
        title="2025 Population vs Charging Station Count Log Scale",
        output_path=FIGURE_DIR / "population_vs_station_count_log.png",
    )

    save_log_scatter_plot(
        country_level,
        x_col="ev_stock",
        y_col="station_count",
        title="2025 EV Stock vs Charging Station Count Log Scale",
        output_path=FIGURE_DIR / "ev_stock_vs_station_count_log.png",
    )

    save_log_scatter_plot(
        country_level,
        x_col="ev_sales",
        y_col="station_count",
        title="2025 EV Sales vs Charging Station Count Log Scale",
        output_path=FIGURE_DIR / "ev_sales_vs_station_count_log.png",
    )
    print("Week 3 EDA finished.")
    print(f"Analysis year: {ANALYSIS_YEAR}")
    print(f"Charging station master shape: {charging.shape}")
    print(f"Country-level analysis shape: {country_level.shape}")

    print()
    print("Top 10 countries by station count:")
    print(
        country_level.sort_values("station_count", ascending=False)
        [
            [
                "country",
                "station_count",
                "tesla_station_record_count",
                "population",
                "gdp",
                "ev_stock",
                "ev_sales",
            ]
        ]
        .head(10)
    )

    print_missing_summary(country_level)
    print_missing_countries(country_level)

    print()
    print("Correlation matrix:")
    print(corr)


if __name__ == "__main__":
    main()