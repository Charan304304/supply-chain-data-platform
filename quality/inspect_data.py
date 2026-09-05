import pandas as pd
from pathlib import Path


DATA_DIR = Path("data/sample")


def inspect_file(filename):
    file_path = DATA_DIR / filename

    df = pd.read_csv(file_path)

    print("\n" + "=" * 60)
    print(f"FILE: {filename}")
    print("=" * 60)

    print(f"Rows       : {len(df):,}")
    print(f"Columns    : {len(df.columns)}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Rows:")
    print(df.duplicated().sum())

    print("\nFirst 5 Records:")
    print(df.head())


if __name__ == "__main__":

    files = [
        "suppliers.csv",
        "products.csv",
        "warehouses.csv",
        "customers.csv",
        "inventory.csv",
        "orders.csv",
        "shipments.csv"
    ]

    for file in files:
        inspect_file(file)