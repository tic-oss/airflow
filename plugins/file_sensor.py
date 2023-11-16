from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from datetime import datetime

with DAG('file_sensor_dag', start_date=datetime(2022, 1, 1)) as dag:
    wait_for_file = FileSensor(
        task_id='wait_for_file',
        fs_conn_id='my_filesystem_conn_id',
        filepath='my_file.txt',
        timeout=600,
        poke_interval=10
    )