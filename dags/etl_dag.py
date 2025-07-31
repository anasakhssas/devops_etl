from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract():
    # Extraction logic ici
    print("Extraction en cours...")

def transform():
    # Transformation logic ici
    print("Transformation en cours...")

def load():
    # Load logic ici
    print("Chargement en cours...")

with DAG(
    'mon_etl',
    start_date=datetime(2024, 6, 1),
    schedule='@daily',  # Remplacez schedule_interval par schedule
    catchup=False
) as dag:
    t1 = PythonOperator(task_id='extract', python_callable=extract)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)

    t1 >> t2 >> t3

if __name__ == "__main__":
    extract()
    transform()
    load()
