import time
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from deferrable_op import WaitOneHourSensor
import pendulum

# Define the DAG
dag = DAG(
    'deferrable',
    schedule_interval=None,
    start_date=pendulum.datetime(2023, 11, 13, tz="UTC"),
)

class WaitOneHourSensor(WaitOneHourSensor): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute_complete(self, context, event=None):
        # Custom logic to execute when the sensor completes
        print("Sensor execution completed")

# Instantiate the custom sensor with deferrable set to True
wait_sensor_deferrable = WaitOneHourSensor(
    task_id='wait_sensor_deferrable',
    deferrable=True,
    dag=dag,
)

# Instantiate the custom sensor with deferrable set to False
wait_sensor_non_deferrable = WaitOneHourSensor(
    task_id='wait_sensor_non_deferrable',
    deferrable=False,
    dag=dag,
)

# Other tasks in the DAG
start_task = DummyOperator(task_id='start', dag=dag)
end_task = DummyOperator(task_id='end', dag=dag)

# Set up task dependencies
start_task >> wait_sensor_deferrable >> end_task
start_task >> wait_sensor_non_deferrable >> end_task
