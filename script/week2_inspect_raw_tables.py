import sqlite3
import pandas as pd

db_path = "data/database/tesla_charging_raw.db"

conn = sqlite3.connect(db_path)

tables = pd.read_sql(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table';
    """,
    conn
)["name"].tolist()

for table in tables:
    print("=" * 80)
    print(f"TABLE: {table}")
    print("=" * 80)

    df = pd.read_sql(f'SELECT * FROM "{table}" LIMIT 5;', conn)

    print("\nColumns:")
    print(list(df.columns))

    print("\nShape preview:")
    row_count = pd.read_sql(f'SELECT COUNT(*) AS n FROM "{table}";', conn)["n"].iloc[0]
    print(f"Rows: {row_count}, Columns: {df.shape[1]}")

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nMissing values in first 5 rows:")
    print(df.isna().sum())

    print("\n")

conn.close()