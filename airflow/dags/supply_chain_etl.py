from datetime import datetime
import sys

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


# ============================================================
# PROJECT PATH
# ============================================================

sys.path.insert(0, "/opt/supply-chain")


# ============================================================
# TASK 1 — CSV INGESTION
# ============================================================

def ingest_csv_data():

    from ingestion.csv_ingestion import ingest_all_csv

    print("=" * 60)
    print("STARTING CSV INGESTION")
    print("=" * 60)

    results = ingest_all_csv()

    print("\nINGESTION SUMMARY")
    print("-" * 60)

    failed = []

    for result in results:

        filename = result.get("filename", "UNKNOWN")
        status = result.get("status", "UNKNOWN")
        records = result.get("records", 0)

        print(
            f"{filename:<20}"
            f"{status:<10}"
            f"{records:,}"
        )

        if status == "FAILED":

            error = result.get(
                "error",
                "Unknown error"
            )

            print(f"ERROR: {error}")

            failed.append(filename)

    print("-" * 60)

    if failed:

        raise RuntimeError(
            f"CSV ingestion failed for {len(failed)} file(s): "
            f"{', '.join(failed)}"
        )

    print(
        "CSV ingestion completed successfully."
    )


# ============================================================
# TASK 2 — ERP INGESTION
# ============================================================

def ingest_erp_data():

    from ingestion.database_ingestion import ingest_erp

    print("=" * 60)
    print("STARTING ERP INGESTION")
    print("=" * 60)

    results = ingest_erp()

    print("\nERP INGESTION SUMMARY")
    print("-" * 60)

    failed = []

    for result in results:

        table = result.get(
            "table",
            "UNKNOWN"
        )

        status = result.get(
            "status",
            "UNKNOWN"
        )

        records = result.get(
            "records",
            0
        )

        print(
            f"{table:<25}"
            f"{status:<10}"
            f"{records:,}"
        )

        if status == "FAILED":

            error = result.get(
                "error",
                "Unknown error"
            )

            print(f"ERROR: {error}")

            failed.append(table)

    print("-" * 60)

    if failed:

        raise RuntimeError(
            f"ERP ingestion failed for "
            f"{len(failed)} table(s): "
            f"{', '.join(failed)}"
        )

    print(
        "ERP ingestion completed successfully."
    )


# ============================================================
# TASK 3 — DATA QUALITY
# ============================================================

def run_data_quality_check():

    from quality.data_quality import run_quality_checks

    print("=" * 60)
    print("STARTING DATA QUALITY CHECK")
    print("=" * 60)

    report = run_quality_checks()

    print("\nDATA QUALITY REPORT")
    print("-" * 60)

    failed = []

    for dataset, checks in report.items():

        print(
            f"\n[{dataset.upper()}]"
        )

        for check, value in checks.items():

            if check == "row_count":
                continue

            if value == 0:

                status = "PASS"

            else:

                status = "FAIL"

                failed.append(
                    f"{dataset}.{check}"
                )

            print(
                f"{check:<40}"
                f"{status:<8}"
                f"{value}"
            )

    print("\n" + "-" * 60)

    if failed:

        raise RuntimeError(
            "Data quality validation failed: "
            + ", ".join(failed)
        )

    print(
        "All data quality checks "
        "passed successfully."
    )


# ============================================================
# TASK 4 — TRANSFORMATIONS
# ============================================================

def run_transformations():

    from scripts.run_transformations import (
        run_all_transformations
    )

    print("=" * 60)
    print("STARTING DATA TRANSFORMATIONS")
    print("=" * 60)

    run_all_transformations()

    print("=" * 60)
    print("DATA TRANSFORMATIONS COMPLETED")
    print("=" * 60)


# ============================================================
# TASK 5 — LOAD DATA WAREHOUSE
# ============================================================

def load_data_warehouse():

    from warehouse.load_warehouse import (
        load_warehouse
    )

    print("=" * 60)
    print("STARTING DATA WAREHOUSE LOAD")
    print("=" * 60)

    load_warehouse()

    print("=" * 60)
    print("DATA WAREHOUSE LOAD COMPLETED")
    print("=" * 60)


# ============================================================
# AIRFLOW DAG
# ============================================================

with DAG(
    dag_id="supply_chain_etl",
    start_date=datetime(2026, 9, 1),
    schedule=None,
    catchup=False,
    tags=["supply-chain", "etl"],
) as dag:

    # --------------------------------------------------------
    # Ingestion
    # --------------------------------------------------------

    ingest_csv = PythonOperator(
        task_id="ingest_csv",
        python_callable=ingest_csv_data,
    )

    ingest_erp = PythonOperator(
        task_id="ingest_erp",
        python_callable=ingest_erp_data,
    )

    # --------------------------------------------------------
    # Data quality
    # --------------------------------------------------------

    data_quality = PythonOperator(
        task_id="data_quality_check",
        python_callable=run_data_quality_check,
    )

    # --------------------------------------------------------
    # Transformations
    # --------------------------------------------------------

    transformations = PythonOperator(
        task_id="transform_data",
        python_callable=run_transformations,
    )

    # --------------------------------------------------------
    # Warehouse loading
    # --------------------------------------------------------

    load_warehouse = PythonOperator(
        task_id="load_warehouse",
        python_callable=load_data_warehouse,
    )

    # --------------------------------------------------------
    # Dependencies
    # --------------------------------------------------------

    [ingest_csv, ingest_erp] >> data_quality

    data_quality >> transformations

    transformations >> load_warehouse