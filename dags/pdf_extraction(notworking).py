import PyPDF2
import airflow
from airflow import DAG
# from airflow.operators.sensors import FileSensor
from airflow.operators.python_operator import PythonOperator

default_args = {
    'start_date': airflow.utils.dates.days_ago(2),
    'retries': 1,
}

dag = DAG('pdf_extracton', default_args=default_args)

def extract_pdf(**kwargs):
    input_file_path = kwargs['/sample.pdf']
    output_file_path = kwargs['/output.txt']

    pdf_reader = PyPDF2.PdfFileReader(input_file_path)
    pdf_writer = PyPDF2.PdfFileWriter()

    for page in pdf_reader.pages:
        pdf_writer.addPage(page)

    with open(output_file_path, 'wb') as f:
        pdf_writer.write(f)

extract_pdf_task = PythonOperator(
    task_id='extract_pdf',
    python_callable=extract_pdf,
    op_kwargs={'input_file_path': '/sample.pdf', 'output_file_path': '/output.txt'},
    dag=dag,
)

# check_file_exists_task = FileSensor(
#     task_id='check_file_exists',
#     filepath='/output.txt',
#     poke_interval=5,
#     timeout=60,
#     dag=dag,
# )

extract_pdf_task #>> check_file_exists_task

if __name__ == '__main__':
    dag.run()