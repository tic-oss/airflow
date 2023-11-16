# add a connection named my_file_system with connection type file and host local 

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime

with DAG('file_sensor_dag', start_date=datetime(2023, 10, 30)) as dag:
    start = DummyOperator(task_id='start')

    is_file_available = FileSensor(
        task_id='is_file_available',
        fs_conn_id='my_file_system',  # optional, if you have a connection defined
        filepath='/home/harika/airflow/dags/sample.pdf',
        poke_interval=10,  # check every 10 seconds
        timeout=60
    )

    end = DummyOperator(task_id='end')

start >> is_file_available >> end