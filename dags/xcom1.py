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

# task1: Executes a Bash command to echo "data" into a file named dummy.txt.
# task2: Executes a Bash command to read and display the content of the dummy.txt file.
# task3: Executes a Bash command to echo "added in task2:" along with the output of task2 using XCom.