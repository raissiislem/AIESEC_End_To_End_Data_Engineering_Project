from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
DOCKER_SCRIPTS_DIR = "/opt/airflow/scripts"

# Make scripts/ importable both when running locally and inside Docker.
for scripts_dir in (LOCAL_SCRIPTS_DIR, DOCKER_SCRIPTS_DIR):
    if os.path.isdir(scripts_dir) and scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

from scraper.scrape_current_month import main as scrape_current_month_main
from bronze.load_bronze import load_file
import psycopg2

DB_CONFIG = {
    "host": "postgres",  # service name, not localhost, since Airflow runs inside Docker's network
    "database": "aiesec_dw",
    "user": "aiesec",
    "password": "aiesec",
    "port": 5432
}


def run_scrape():
    output_path = scrape_current_month_main()
    return output_path  # passed to next task via XCom


def load_bronze_from_path(file_path):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    rows_loaded = load_file(cur, file_path)
    conn.commit()
    cur.close()
    conn.close()
    print(f"✔ Loaded {rows_loaded} rows from {file_path}")


def run_load_bronze(**context):
    file_path = context["ti"].xcom_pull(task_ids="scrape_current_month")
    load_bronze_from_path(file_path)


default_args = {
    "owner": "aiesec_tunisia",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_scrape_and_load",
    default_args=default_args,
    description="Scrape current month AIESEC data, load to Bronze, run dbt",
    schedule_interval="@daily",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["aiesec", "scraping", "dbt"],
) as dag:

    scrape_task = PythonOperator(
        task_id="scrape_current_month",
        python_callable=run_scrape,
    )

    load_bronze_task = PythonOperator(
        task_id="load_bronze",
        python_callable=run_load_bronze,
    )

    dbt_run_task = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "dbt run "
            "--project-dir /opt/airflow/dbt/aiesec_tunisia "
            "--profiles-dir /opt/airflow/dbt_profiles"
        ),
    )

    scrape_task >> load_bronze_task >> dbt_run_task


def main():
    print("Running daily_scrape_and_load locally...")
    output_path = run_scrape()
    load_bronze_from_path(output_path)
    print("Local run completed. The Airflow DAG definition is still available for scheduler execution.")


if __name__ == "__main__":
    main()