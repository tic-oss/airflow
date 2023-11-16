# https://gorillalogic.com/blog/you-can-easily-build-a-scalable-data-pipeline-with-apache-airflow-heres-how

from airflow.models import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator

from datetime import datetime

# define the dag with an ID, schedule interval and start date
dag = DAG(
  'first_dag',
  schedule_interval='@daily',
  start_date=datetime(2022, 10, 18)
)
# --------- DAG is now set up and ready to run -------------

#***************************************************************************
# adding tasks to fetch a random integer between 1 to 10 
# since we are interacting with API,we'll need to add HTTP connection first
#in airflow dashboard Admin -> connections -> + -> id :  random_data_default, type : HTTP, host: http://random-data-api.com/api
#***************************************************************************

# creating tasks using http operator
# model_a = SimpleHttpOperator(
#   task_id='model_a',
#   method='GET',
#   endpoint='number/random_number',
#   http_conn_id='random_data_default',
#   response_filter=lambda response: response.json()['digit'],
#   dag=dag
# )

# model_b = SimpleHttpOperator(
#   task_id='model_b',
#   method='GET',
#   endpoint='number/random_number',
#   http_conn_id='random_data_default',
#   response_filter=lambda response: response.json()['digit'],
#   dag=dag
# )

# Define a reusable function to create SimpleHttpOperator tasks
def create_http_task(task_id):
    return SimpleHttpOperator(
        task_id=task_id,
        method='GET',
        endpoint='number/random_number',
        http_conn_id='random_data_default',
        response_filter=lambda response: response.json()['digit'],
        dag=dag
    )

# Create model_a and model_b tasks using the create_http_task function
model_a = create_http_task('model_a')
model_b = create_http_task('model_b')

# define branching function
# '''branching''' making it more maintainable and flexible
# It retrieves XCom values (results) from model_a and model_b tasks and 
#decides whether to proceed to an "accurate" or "inaccurate" branch based on a condition (in this case, whether the maximum accuracy is greater than 7).
# The ti parameter is specific to the task instance and 
#provides context and information related to the current task being executed.(we can use any var also)
def _check_accuracy(ti):
  accuracies = ti.xcom_pull(task_ids=['model_a', 'model_b'])
  return 'accurate' if max(accuracies) > 7 else 'inaccurate'

# create BranchPythonOperator
# integrate a '''Python function''' for dynamic decision-making
# check_accuracy is a BranchPythonOperator task. It uses the _check_accuracy Python function as its branching logic. The provide_context=True parameter is 
# set to allow access to XCom values in the Python function.

#************************************************************************
# This operator takes the XCom values produced by model_a and model_b. 
#It then calls the _check_accuracy Python function to determine which task should be
#executed next based on the accuracy values from model_a and model_b.
check_accuracy = BranchPythonOperator(
  task_id='check_accuracy',
  python_callable=_check_accuracy,
  provide_context=True,  # This is required to access XCom values
  dag=dag
)

# creating tasks using bashOperator
accurate = BashOperator(
  task_id="accurate",
  bash_command="echo 'accurate'",
  dag=dag
)

inaccurate = BashOperator(
  task_id="inaccurate",
  bash_command="echo 'inaccurate'",
  dag=dag
)

# define task dependencies
model_a >> check_accuracy
model_b >> check_accuracy
check_accuracy >> [accurate, inaccurate]
