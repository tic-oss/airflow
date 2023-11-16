from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
# pip install PyPDF2
import PyPDF2
# from config.config import sample_pdf_file_path 

sample_pdf_file_path = '/home/harika/airflow/dags/sample.pdf'

# Define a Python function for extracting text from a PDF file
def extract_text_from_pdf(pdf_file_path, **kwargs):
    pdf_file = open(pdf_file_path, 'rb')
    try:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)

        text = ''
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()

        return text
    except Exception as e:
        return None
    finally:
        pdf_file.close()

# Define your Airflow DAG
dag = DAG(
    'pdf_extract',
    description='Extract text from a PDF file',
    schedule_interval=None,  # Define your schedule interval here
    start_date=datetime(2023, 10, 13),
    catchup=False,
)

# Define a task that extracts text from the PDF
extract_text_task = PythonOperator(
    task_id='extract_text_from_pdf',
    python_callable=extract_text_from_pdf,
    # op_args=[sample_pdf_file_path],  # Provide the path to your PDF file
    op_args=[sample_pdf_file_path],  # Provide the path to your PDF file
    provide_context=True,
    dag=dag,
)

# Set up task dependencies
extract_text_task

if __name__ == "__main__":
    dag.cli()
