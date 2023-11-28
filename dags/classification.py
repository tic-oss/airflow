from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta
from airflow.utils.dates import days_ago
from airflow.operators.dummy_operator import DummyOperator
import openai
import time
from datetime import datetime

dag = DAG('classification', start_date=datetime(2023,11,22), description='Determine the topic of the text')

def summarize_code(file_path):
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

summarize_wiki_data_task = PythonOperator(
    task_id='summarize_wiki_data_task',
    python_callable=summarize_code,
    op_kwargs={'file_path': '/home/harika/wikidata/content.txt'},
    dag=dag
)

start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

start >> summarize_wiki_data_task >> end
