from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.dummy_operator import DummyOperator
import openai
import time
from datetime import datetime

dag = DAG('classification_email', start_date=datetime(2023,11,27), description='Determine the topic of the text')

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

EMAIL = 'harikasree2225@gmail.com'
def send_email_with_topic(task_instance, topic_name, **kwargs):
    email_task = EmailOperator(
        task_id='send_extracted_topic_email', 
        to=EMAIL,
        subject='Wiki topic extracted',
        html_content=f'<p> {topic_name} </p>',
        dag=dag
    )
    # passing the entire dictionary of context variables to the execute method of the EmailOperator.
    #  This ensures that the downstream task (EmailOperator) has access to the same context as the task that is calling it, including things like the execution date, task instance, and XCom values.
    email_task.execute(context=kwargs)

summarize_wiki_data_task = PythonOperator(
    task_id='summarize_wiki_data_task',
    python_callable=summarize_code,
    op_kwargs={'file_path': '/home/harika/wikidata/content.txt'},
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

start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

start >> summarize_wiki_data_task >> send_email_with_topic_task >> end