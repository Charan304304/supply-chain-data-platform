from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def check_environment():
    print("======================================")
    print("SUPPLY CHAIN DATA PLATFORM")
    print("======================================")
    print("Airflow is working!")
    print("Python execution successful.")


def check_project_structure():
    print("Checking project structure...")
    print("Data Engineering pipeline is ready.")


with DAG(
    dag_id="supply_chain_test",
    start_date=datetime(2026, 9, 1),
    schedule=None,
    catchup=False,
    tags=["supply-chain", "test"],
) as dag:

    environment_check = PythonOperator(
        task_id="check_environment",
        python_callable=check_environment,
    )

    structure_check = PythonOperator(
        task_id="check_project_structure",
        python_callable=check_project_structure,
    )

    environment_check >> structure_check