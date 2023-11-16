from airflow.operators.python_operator import PythonOperator
import airflow
from airflow import DAG

def push_function(**context):
    context['ti'].xcom_push(key='my_key', value='my_value')

default_args = {
    'start_date': airflow.utils.dates.days_ago(2),
    'retries': 1,
}
dag = DAG('xcomBasic', default_args=default_args, description='xCom basic')

def pull_function(**context):
    context['ti'].xcom_pull(key='my_key', task_ids='push_task')

push_task = PythonOperator(
    task_id='push_task',
    python_callable=push_function,
    provide_context=True,
    dag=dag,
)

pull_task = PythonOperator(
    task_id='pull_task',
    python_callable=pull_function,
    provide_context=True,
    dag=dag,
)

push_task >> pull_task