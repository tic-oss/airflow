from airflow.operators.python_operator import PythonOperator
import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'start_date': airflow.utils.dates.days_ago(2),
    'retries': 1,
}
dag = DAG('xcomEx1', default_args=default_args, description='xCom example')

task1 = BashOperator(
    task_id='task1',
    bash_command='echo "data" > /home/harika/airflow/dags/dummy.txt',
    dag=dag)

task2 = BashOperator(
    task_id='task2',
    bash_command='cat /home/harika/airflow/dags/dummy.txt',
    dag=dag)

task3 = BashOperator(
    task_id='task3',
    bash_command='echo "added in task2:" {{ ti.xcom_pull(task_ids="task2") }}',
    dag=dag)

task1 >> task2 >> task3