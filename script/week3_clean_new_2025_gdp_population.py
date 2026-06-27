from pathlib import Path

import pandas as pd


EXTERNAL_DIR = Path("data/external/economy_factor_data")
PROCESSED_DIR = Path("data/processed")

POP_INPUT = EXTERNAL_DIR / "World_Population_ByCountry.csv"
GDP_INPUT = EXTERNAL_DIR / "World_GDP_ByCountry.csv"

POP_OUTPUT = PROCESSED_DIR / "world_population_bycountry_2025_cleaned.csv"
GDP_OUTPUT = PROCESSED_DIR / "world_gdp_bycountry_2025_cleaned.csv"


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


def clean_country_key(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.lower()
    )
    return cleaned.replace(COUNTRY_NAME_MAPPING)

def read_csv_with_encoding_fallback(path: Path) -> pd.DataFrame:
    """
    Read CSV with multiple encoding attempts.
    Some external GDP/population files are not UTF-8 encoded.
    """
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1", "ISO-8859-1"]

    last_error = None

    for encoding in encodings:
        try:
            print(f"Trying to read {path.name} with encoding: {encoding}")
            return pd.read_csv(path, low_memory=False, encoding=encoding)
        except UnicodeDecodeError as error:
            last_error = error
            print(f"Failed with encoding: {encoding}")

    raise UnicodeDecodeError(
        "encoding_fallback",
        b"",
        0,
        1,
        f"Unable to read {path} with tested encodings. Last error: {last_error}",
    )


def clean_numeric(series: pd.Series) -> pd.Series:
    """
    Convert messy numeric strings into numbers.
    Handles commas, percent signs, mojibake symbols, and 'no data'.
    """
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace("âˆ’", "-", regex=False)
        .str.replace("−", "-", regex=False)
        .str.replace(r"[^\d\.\-]", "", regex=True)
    )

    cleaned = cleaned.replace("", pd.NA)
    return pd.to_numeric(cleaned, errors="coerce")


def find_column_by_keywords(columns: list[str], keywords: list[str]) -> str:
    """
    Find the first column whose lower-case name contains all keywords.
    """
    for col in columns:
        col_lower = str(col).lower()
        if all(keyword.lower() in col_lower for keyword in keywords):
            return col
    raise ValueError(f"Cannot find column with keywords: {keywords}")


def clean_population() -> pd.DataFrame:
    pop = read_csv_with_encoding_fallback(POP_INPUT)

    pop.columns = [str(col).strip() for col in pop.columns]

    country_col = find_column_by_keywords(pop.columns.tolist(), ["country"])
    population_col = find_column_by_keywords(pop.columns.tolist(), ["population", "2025"])

    pop_cleaned = pop[[country_col, population_col]].copy()
    pop_cleaned = pop_cleaned.rename(
        columns={
            country_col: "country_name",
            population_col: "population",
        }
    )

    pop_cleaned["country_name"] = pop_cleaned["country_name"].astype(str).str.strip()
    pop_cleaned["country_key"] = clean_country_key(pop_cleaned["country_name"])
    pop_cleaned["year"] = 2025
    pop_cleaned["population"] = clean_numeric(pop_cleaned["population"])
    pop_cleaned["source"] = "world_population_bycountry_2025"

    pop_cleaned = pop_cleaned.dropna(subset=["country_key", "population"])
    pop_cleaned = pop_cleaned.drop_duplicates(subset=["country_key", "year"])

    pop_cleaned = pop_cleaned[
        [
            "country_key",
            "country_name",
            "year",
            "population",
            "source",
        ]
    ]

    pop_cleaned.to_csv(POP_OUTPUT, index=False)

    print("Population 2025 cleaned.")
    print(f"Input: {POP_INPUT}")
    print(f"Output: {POP_OUTPUT}")
    print(f"Shape: {pop_cleaned.shape}")

    return pop_cleaned


def clean_gdp() -> pd.DataFrame:
    gdp = read_csv_with_encoding_fallback(GDP_INPUT)

    gdp.columns = [str(col).strip() for col in gdp.columns]

    # The first column is country name, but its title may be:
    # "GDP, current prices (Billions of U.S. dollars)"
    country_col = gdp.columns[0]

    if "2025" not in gdp.columns:
        raise ValueError("The GDP file does not contain a 2025 column.")

    gdp_cleaned = gdp[[country_col, "2025"]].copy()
    gdp_cleaned = gdp_cleaned.rename(
        columns={
            country_col: "country_name",
            "2025": "gdp_billion_usd",
        }
    )

    gdp_cleaned["country_name"] = gdp_cleaned["country_name"].astype(str).str.strip()
    gdp_cleaned["country_key"] = clean_country_key(gdp_cleaned["country_name"])
    gdp_cleaned["year"] = 2025

    # Original file unit is billions of U.S. dollars.
    gdp_cleaned["gdp_billion_usd"] = clean_numeric(gdp_cleaned["gdp_billion_usd"])

    # Keep the original project convention: gdp = current US dollars.
    # Example: 28750.96 billion -> 2.875096e13 dollars.
    gdp_cleaned["gdp"] = gdp_cleaned["gdp_billion_usd"] * 1_000_000_000

    gdp_cleaned["source"] = "world_gdp_bycountry_2025"

    gdp_cleaned = gdp_cleaned.dropna(subset=["country_key", "gdp"])
    gdp_cleaned = gdp_cleaned.drop_duplicates(subset=["country_key", "year"])

    gdp_cleaned = gdp_cleaned[
        [
            "country_key",
            "country_name",
            "year",
            "gdp_billion_usd",
            "gdp",
            "source",
        ]
    ]

    gdp_cleaned.to_csv(GDP_OUTPUT, index=False)

    print("GDP 2025 cleaned.")
    print(f"Input: {GDP_INPUT}")
    print(f"Output: {GDP_OUTPUT}")
    print(f"Shape: {gdp_cleaned.shape}")

    return gdp_cleaned


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    pop_cleaned = clean_population()
    gdp_cleaned = clean_gdp()

    print()
    print("Sample cleaned population:")
    print(pop_cleaned.head(10))

    print()
    print("Sample cleaned GDP:")
    print(gdp_cleaned.head(10))


if __name__ == "__main__":
    main()