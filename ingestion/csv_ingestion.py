import pandas as pd
from pathlib import Path
from datetime import datetime

from ingestion.metadata import log_ingestion


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

# Project root inside the Airflow Docker container
PROJECT_ROOT = Path("/opt/supply-chain")

SOURCE_DIR = PROJECT_ROOT / "data" / "sample"
RAW_DIR = PROJECT_ROOT / "data" / "raw"


# Make sure the raw directory exists
RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# INGEST ONE CSV FILE
# ============================================================

def ingest_csv(filename):
    """
    Read a CSV source file and copy it
    into the raw data layer.
    """

    source_path = SOURCE_DIR / filename
    raw_path = RAW_DIR / filename

    print(f"Reading: {source_path}")

    df = pd.read_csv(source_path)

    df.to_csv(
        raw_path,
        index=False
    )

    print(
        f"Loaded {len(df):,} records "
        f"into {raw_path}"
    )

    log_ingestion(
        filename=filename,
        records=len(df),
        status="SUCCESS"
    )

    return {
        "filename": filename,
        "records": len(df),
        "ingestion_time": datetime.now(),
        "status": "SUCCESS"
    }


# ============================================================
# INGEST ALL CSV FILES
# ============================================================

def ingest_all_csv():

    files = [
        "suppliers.csv",
        "products.csv",
        "warehouses.csv",
        "customers.csv",
        "inventory.csv",
        "orders.csv",
        "shipments.csv"
    ]

    results = []

    for filename in files:

        try:

            result = ingest_csv(filename)

            results.append(result)

        except Exception as error:

            results.append({
                "filename": filename,
                "records": 0,
                "ingestion_time": datetime.now(),
                "status": "FAILED",
                "error": str(error)
            })

    return results


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("SUPPLY CHAIN CSV INGESTION")
    print("=" * 60)

    results = ingest_all_csv()

    print("\nINGESTION SUMMARY")
    print("-" * 60)

    for result in results:

        print(
            f"{result['filename']:<20}"
            f"{result['status']:<10}"
            f"{result['records']:,}"
        )

        if result["status"] == "FAILED":
            print(
                f"ERROR: "
                f"{result.get('error', 'Unknown error')}"
            )