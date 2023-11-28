from datetime import timedelta
import wikipedia
from airflow import DAG
import os
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.email_operator import EmailOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.utils.dates import days_ago
from airflow.utils.edgemodifier import Label

DOWNLOAD_LOCATION = '/home/harika/wikidata'
TOPIC_NAME = 'Kerala'
EMAIL = 'harikasree2225@gmail.com'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': [EMAIL],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('wiki_limit_dag', default_args=default_args, description='A multi step DAG to download Wikipedia content and count words', schedule_interval=timedelta(days=1))

def get_details_from_wikipedia_api(topic):
    print(topic)
    page = wikipedia.page(topic)
    print(page.title)
    content = page.content

    sliced_content = content[:450]
    download_folder = os.path.join(DOWNLOAD_LOCATION, topic)
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    file_location = os.path.join(download_folder, 'content.txt')
    with open(file_location, 'w') as f:
        f.write(sliced_content)

    return file_location

def send_processed_file_as_email(**context):
    input_file_location = context['ti'].xcom_pull(task_ids='get_details_from_wikipedia_task')
    print(f'Input file location: {input_file_location}')
    output_file_location = input_file_location.replace('.txt', '_counts.csv')
    print(f'Output file location: {output_file_location}')

    processed_email_task = EmailOperator(
        task_id = 'send_processed_email',
        to = EMAIL, 
        subject = 'Wiki entry processed',
        html_content = '<p> Wiki entry processed. </p>',
        files = [output_file_location],
        dag = dag
    )

    processed_email_task.execute(context)

get_details_from_wikipedia_task = PythonOperator(
        task_id='get_details_from_wikipedia_task', 
        python_callable=get_details_from_wikipedia_api,
        op_kwargs={'topic': TOPIC_NAME},
        dag=dag
)

email_task = EmailOperator(
    task_id = 'send_notification_email',
    to = EMAIL,
    subject = 'Wiki entry downloaded',
    html_content = '<p> Wiki entry downloaded. </p>',
    dag = dag
)

spark_submit_task = SparkSubmitOperator(
    task_id = 'submit_spark_word_count_job',
    name = 'PythonWordCount',
    application = '/home/harika/sparkjobs/word_count_extended.py',
    application_args = ["{{ task_instance.xcom_pull(task_ids='get_details_from_wikipedia_task') }}"],
    dag=dag
)

send_processed_file_as_email_task = PythonOperator(
        task_id='send_processed_file_as_email', 
        python_callable=send_processed_file_as_email,
        provide_context=True,
        dag=dag
)

start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

# start >> Label("Fetch data") >> get_details_from_wikipedia_task >> Label("Send mail as data is downloaded and count words") >> [email_task, spark_submit_task] >> Label("Send mail of processed data") >> send_processed_file_as_email_task >> Label("Mail sent") >> end
start >> Label("Fetch data") >> get_details_from_wikipedia_task 
get_details_from_wikipedia_task >> Label("send mail as data downloaded") >> email_task
get_details_from_wikipedia_task >> Label("count words") >> spark_submit_task
email_task >> Label("send mail as data processed") >> send_processed_file_as_email_task
spark_submit_task >> Label("send mail of counted words as file") >> send_processed_file_as_email_task
send_processed_file_as_email_task >> Label("Mail sent") >> end
