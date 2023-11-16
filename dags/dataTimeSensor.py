from airflow.sensors.date_time_sensor import DateTimeSensor
from airflow import DAG
from datetime import datetime

dag = DAG(dag_id="date_time_sensor", schedule_interval="20 10 * * *", start_date=datetime(2023, 11, 8))

time_sensor = DateTimeSensor(
    task_id='wait_until_time',
    target_time='2023-11-08T07:07:00',
    mode="reschedule",
    dag=dag, 
)
