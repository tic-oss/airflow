from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
import openai
import time
from datetime import datetime
import os

dag = DAG('unstructured_data', start_date=datetime(2023,12,12), description='Data Pipeline for unstructured data')

def openai_interaction(file_path, prompt, output_file):
    openai.api_key = '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'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(file_path, 'r') as file:
        code = file.read()
    if len(code.split()) > 4097:
        code = ' '.join(code.split()[:4097])
    try:
        response = openai.completions.create(
            model="text-davinci-003",
            prompt=prompt.format(code),
            max_tokens=2000,
            temperature=0.7,
            n=1,
            timeout=10,
        )
        if response and response.choices:
            with open(output_file, 'w') as output:
                output.write(str(response.choices[0].text.strip()))
            return response.choices[0].text.strip()
    except openai.RateLimitError as e:
        print(f"Rate limit exceeded. Waiting for {e.retry_after} seconds.")
        time.sleep(e.retry_after)
        return openai_interaction(file_path, prompt, output_file)
    except Exception as ex:
        print(f"An error occurred: {ex}")
        with open(output_file, 'w') as output:
            output.write("Error: Unable to generate a summary.")

def fetch_topic(file_path, output_file):
    prompt = 'What is the topic of the text: {}'
    return openai_interaction(file_path, prompt, output_file)

def create_questions(file_path, output_file):
    prompt = 'create 10 questions from the text: {}'
    return openai_interaction(file_path, prompt, output_file)

def generate_answers(file_path, output_file, **kwargs):
    ti = kwargs['ti']
    questions_output = ti.xcom_pull(task_ids='create_questions_task')
    prompt = f'generate answers for the questions : {questions_output}'
    return openai_interaction(file_path, prompt, output_file)

input_file_path = '/home/harika/wikidata/content.txt'
output_folder = '/home/harika/wikidata/unstructured_dag'

fetch_topic_task = PythonOperator(
    task_id='fetch_topic_task',
    python_callable=fetch_topic,
    op_kwargs={'file_path': input_file_path, 'output_file': f'{output_folder}/fetch_topic.txt'},
    dag=dag
)

create_questions_task = PythonOperator(
    task_id='create_questions_task',
    python_callable=create_questions,
    op_kwargs={'file_path': input_file_path, 'output_file': f'{output_folder}/create_questions.txt'},
    dag=dag
)

generate_answers_task = PythonOperator(
    task_id='generate_answers_task',
    python_callable=generate_answers,
    op_kwargs={'file_path': input_file_path, 'output_file': f'{output_folder}/generate_answers.txt'},
    provide_context=True,
    dag=dag
)

start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

start >> fetch_topic_task >> create_questions_task >> generate_answers_task >> end
