import sqlite3
import pandas as pd
from pathlib import Path

from ingestion.metadata import log_ingestion


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

PROJECT_ROOT = Path("/opt/supply-chain")

DATABASE_PATH = PROJECT_ROOT / "data" / "source_system" / "erp.db"
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "erp"


# Make sure the ERP raw directory exists
RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# INGEST ONE ERP TABLE
# ============================================================

def ingest_table(table_name):

    print(
        f"Extracting ERP table: {table_name}"
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        query = f"SELECT * FROM {table_name}"

        df = pd.read_sql(
            query,
            connection
        )

    finally:

        connection.close()

    output_file = RAW_DIR / f"{table_name}.csv"

    df.to_csv(
        output_file,
        index=False
    )

    log_ingestion(
        filename=f"erp/{table_name}.csv",
        records=len(df),
        status="SUCCESS"
    )

    print(
        f"Loaded {len(df):,} records "
        f"into {output_file}"
    )

    return {
        "table": table_name,
        "records": len(df),
        "status": "SUCCESS"
    }


# ============================================================
# INGEST ALL ERP TABLES
# ============================================================

def ingest_erp():

    tables = [
        "supplier_master",
        "product_master",
        "warehouse_master",
        "purchase_orders"
    ]

    results = []

    for table in tables:

        try:

            result = ingest_table(table)

            results.append(result)

        except Exception as error:

            print(
                f"ERROR: {table}: {error}"
            )

            log_ingestion(
                filename=f"erp/{table}.csv",
                records=0,
                status="FAILED",
                error=str(error)
            )

            results.append({
                "table": table,
                "records": 0,
                "status": "FAILED",
                "error": str(error)
            })

    return results


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ERP DATABASE INGESTION")
    print("=" * 60)

    results = ingest_erp()

    print("\nERP INGESTION SUMMARY")
    print("-" * 60)

    for result in results:

        print(
            f"{result['table']:<25}"
            f"{result['status']:<10}"
            f"{result['records']:,}"
        )

        if result["status"] == "FAILED":

            print(
                f"ERROR: "
                f"{result.get('error', 'Unknown error')}"
            )

    print("-" * 60)
    print("ERP ingestion completed.")