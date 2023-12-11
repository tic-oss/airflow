from datetime import timedelta
import os
# pip install requests
# pip install beautifulsoup4
import requests
from bs4 import BeautifulSoup

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.email_operator import EmailOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago

DOWNLOAD_LOCATION = '/home/harika/webdata'
URL = 'https://www.toptal.com/spark/introduction-to-apache-spark#:~:text=Spark%20introduces%20the%20concept%20of,collection%20from%20the%20driver%20program.'  # Replace with the desired URL
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

dag = DAG('webpage_dag', default_args=default_args, description='A multi-step DAG to download web page content and count words', schedule_interval=timedelta(days=1))

# use Python libraries like requests and BeautifulSoup for web scraping
# The soup.get_text() method extracts only the text content and discards HTML tags.
def get_details_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        page_content = response.text
        soup = BeautifulSoup(page_content, 'html.parser')
        content = soup.get_text()
        download_folder = os.path.join(DOWNLOAD_LOCATION, 'web_page_data')
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        file_location = os.path.join(download_folder, 'content.txt')
        with open(file_location, 'w') as f:
            f.write(content)
        return file_location
    else:
        return None

def send_processed_file_as_email(**context):
    input_file_location = context['ti'].xcom_pull(task_ids='get_details_from_url_task')
    print(f'Input file location: {input_file_location}')
    output_file_location = input_file_location.replace('.txt', '_counts.csv')
    print(f'Output file location: {output_file_location}')

    processed_email_task = EmailOperator(
        task_id='send_processed_email',
        to=EMAIL,
        subject='Webpage content processed',
        html_content='<p>Webpage content processed.</p>',
        files=[output_file_location],
        dag=dag
    )

    processed_email_task.execute(context)

get_details_from_url_task = PythonOperator(
    task_id='get_details_from_url_task',
    python_callable=get_details_from_url,
    op_kwargs={'url': URL},
    provide_context=True,
    dag=dag
)

email_task = EmailOperator(
    task_id='send_notification_email',
    to=EMAIL,
    subject='Webpage content downloaded',
    html_content='<p>Webpage content downloaded.</p>',
    dag=dag
)

spark_submit_task = SparkSubmitOperator(
    task_id='submit_spark_word_count_job',
    name='PythonWordCount',
    application='/home/harika/sparkjobs/word_count_extended.py',
    application_args=["{{ task_instance.xcom_pull(task_ids='get_details_from_url_task') }}"],
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

start >> get_details_from_url_task >> [email_task, spark_submit_task] >> send_processed_file_as_email_task >> end
