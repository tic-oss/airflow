from airflow import DAG
from datetime import datetime, timedelta
from demo_plugin import DataTransferOperator, FileCountSensor , MySQLToPostgresHook
#calling hooks- create task using python operator and then import method function instead of custom_hook
from airflow.operators.python_operator import PythonOperator

dag = DAG("plugin_dag", schedule_interval=timedelta(1), start_date=datetime(2023,10,31), catchup=False)

def trigger_hook():
    MySQLToPostgresHook().copy_table('mysql_conn', 'postgres_conn')
    print('done')

t1 = DataTransferOperator(
    task_id = "data_transfer",
    source_file_path = "/home/harika/airflow/plugins/source.txt",
    dest_file_path = "/home/harika/airflow/plugins/destination.txt",
    delete_list = ["Airflow", "is"],
    dag = dag
)

t2 = FileCountSensor(
    task_id = "file_count_sensor",
    dir_path = '/home/harika/airflow/plugins',
    conn_id = 'fs_default',
    poke_interval = 10,
    timeout = 60,
    dag = dag
)

t3 = PythonOperator(
    task_id = "mysql_to_postgres",
    python_callable = trigger_hook,
    dag = dag
)

t1 >> t2 >> t3