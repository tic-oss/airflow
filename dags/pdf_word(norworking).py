from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import PyPDF2
import re

# Define a Python function for counting word occurrences in a PDF file
def count_word_occurrences(pdf_file_path, target_word, **kwargs):
    try:
        pdf_file = open(pdf_file_path, 'rb')
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)

        text = ''
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()

        # Use regular expressions to split the text into words
        words = re.findall(r'\b\w+\b', text)

        # Count the occurrences of the target word
        word_count = words.count(target_word)

        print(f"The word '{target_word}' occurs {word_count} times in the PDF.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pdf_file.close()

# Define your Airflow DAG
dag = DAG(
    'pdf_word_count_dag',
    description='Count word occurrences in a PDF file',
    schedule_interval=None,  # Define your schedule interval here
    start_date=datetime(2023, 10, 13),
    catchup=False,
)

# Define a task to count word occurrences in the PDF
count_word_occurrences_task = PythonOperator(
    task_id='count_word_occurrences_in_pdf',
    python_callable=count_word_occurrences,
    op_args=['/sample.pdf', 'Simple'],  # Provide the path to your PDF file and the target word
    provide_context=True,
    dag=dag,
)

# Set up task dependencies
count_word_occurrences_task

if __name__ == "__main__":
    dag.cli()
