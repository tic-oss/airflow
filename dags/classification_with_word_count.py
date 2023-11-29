from datetime import timedelta
import wikipedia
from airflow import DAG
import os
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.email_operator import EmailOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import datetime
import openai
import time

DOWNLOAD_LOCATION = '/home/harika/wikidata'
TOPIC_NAME = 'Hyderabad'
EMAIL = 'harikasree2225@gmail.com'

dag = DAG('classification_with_word_count', start_date=datetime(2023,11,27), description='A multi step DAG to download Wikipedia content and count words', schedule_interval=timedelta(days=1))

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

def summarize_code(file_path, **kwargs):
    openai.api_key = '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'
    with open(file_path, 'r') as file:
        code = file.read()
    if len(code.split()) > 4097:
        code = ' '.join(code.split()[:4097])
    prompt = f"what is the topic of the text: {code}"
    try:
        response = openai.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=2000, 
            temperature=0.7,
            n=1,
            timeout=10,
        )
        if response and response.choices:
            print('######################',response.choices[0].text.strip())
            return response.choices[0].text.strip()
    except openai.RateLimitError as e:
        print(f"Rate limit exceeded. Waiting for {e.retry_after} seconds.")
        time.sleep(e.retry_after)
        return summarize_code(file_path)
    return "Error: Unable to generate a summary."

def send_email_with_topic(task_instance, topic_name, **kwargs):
    email_task = EmailOperator(
        task_id='send_extracted_topic_email', 
        to=EMAIL,
        subject='Wiki topic extracted',
        html_content=f'<p> {topic_name} </p>',
        dag=dag
    )
    email_task.execute(context=kwargs)



summarize_wiki_data_task = PythonOperator(
    task_id='summarize_wiki_data_task',
    python_callable=summarize_code,
     op_kwargs={'file_path': "{{ task_instance.xcom_pull(task_ids='get_details_from_wikipedia_task') }}"},
    provide_context=True,
    dag=dag
)

send_email_with_topic_task = PythonOperator(
    task_id='send_email_topic',  
    python_callable=send_email_with_topic,
    op_kwargs={'topic_name': '{{ task_instance.xcom_pull(task_ids="summarize_wiki_data_task") }}'},
    provide_context=True,
    dag=dag
)

start >> get_details_from_wikipedia_task
get_details_from_wikipedia_task >> summarize_wiki_data_task >> send_email_with_topic_task >> send_processed_file_as_email_task
get_details_from_wikipedia_task >> email_task >> send_processed_file_as_email_task
get_details_from_wikipedia_task >> spark_submit_task >>send_processed_file_as_email_task
send_processed_file_as_email_task >> end

