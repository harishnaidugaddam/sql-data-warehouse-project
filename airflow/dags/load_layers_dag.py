from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': False
}

with DAG(
    dag_id='load_datawarehouse_layers',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    description='ETL Pipeline: Bronze -> Silver -> Gold'
) as dag:

    load_bronze = BashOperator(
        task_id='load_bronze_layer',
        bash_command="""
        docker run --rm \
          --network host \
          mcr.microsoft.com/mssql-tools \
          /opt/mssql-tools/bin/sqlcmd \
          -S host.docker.internal -U sa -P 'YourStrong!Passw0rd' -d DataWarehouse \
          -Q "EXEC bronze.load_bronze"
        """
    )

    load_silver = BashOperator(
        task_id='load_silver_layer',
        bash_command="""
        docker run --rm \
          --network host \
          mcr.microsoft.com/mssql-tools \
          /opt/mssql-tools/bin/sqlcmd \
          -S host.docker.internal -U sa -P 'YourStrong!Passw0rd' -d DataWarehouse \
          -Q "EXEC silver.load_silver"
        """
    )

    gold_note = BashOperator(
        task_id='gold_layer_info',
        bash_command='echo "Gold layer uses pre-created views. No load step needed."'
    )

    load_bronze >> load_silver >> gold_note

dag = dag
