from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime


with DAG(
    dag_id="transaction_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    validate_transactions = BashOperator(
        task_id="validate_transactions",
        bash_command="python /opt/airflow/scripts/validate_transactions.py",
    )

    load_transactions = BashOperator(
        task_id="load_transactions",
        bash_command="python /opt/airflow/scripts/load_transactions.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "mkdir -p /tmp/dbt-target /tmp/dbt-logs && "
            "dbt run "
            "--project-dir /opt/airflow/dbt "
            "--profiles-dir /opt/airflow/dbt/profiles "
            "--target-path /tmp/dbt-target "
            "--log-path /tmp/dbt-logs"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "mkdir -p /tmp/dbt-target /tmp/dbt-logs && "
            "dbt test "
            "--project-dir /opt/airflow/dbt "
            "--profiles-dir /opt/airflow/dbt/profiles "
            "--target-path /tmp/dbt-target "
            "--log-path /tmp/dbt-logs"
        ),
    )

    validate_transactions >> load_transactions >> dbt_run >> dbt_test
