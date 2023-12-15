from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
import pandas as pd
from datetime import datetime
import os

dag = DAG('structured_data', start_date=datetime(2023, 12, 12), description='Data Pipeline for structured data')

def filtered_data(input_file_path, output_file, filter_column, filter_operation, filter_value, **kwargs):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df = pd.read_csv(input_file_path)
    is_numeric = pd.api.types.is_numeric_dtype(df[filter_column])
    if is_numeric:
        filter_value = float(filter_value)
        filter_functions = {
            '<': lambda x: x < filter_value,
            '>': lambda x: x > filter_value,
            '<=': lambda x: x <= filter_value,
            '>=': lambda x: x >= filter_value,
            '==': lambda x: x == filter_value,
            '=': lambda x: x == filter_value,
        }
        if filter_operation in filter_functions:
            filtered_df = df[filter_functions[filter_operation](df[filter_column])]
        else:
            raise ValueError(f"Unsupported numeric comparison operator: {filter_operation}")
    else:
        filtered_df = df[df[filter_column] == filter_value]

    filtered_df.to_csv(output_file, index=False)
    kwargs['ti'].xcom_push(key='output_file', value=output_file)

def sorted_data(input_file_path, output_file, sort_column, **kwargs):
    df = pd.read_csv(input_file_path)
    sorted_df = df.sort_values(by=sort_column, ascending=True)
    sorted_df.to_csv(output_file, index=False)
    kwargs['ti'].xcom_push(key='output_file', value=output_file)

def aggregate_data(input_file_path, output_file, aggregation_column, aggregation_operation):
    df = pd.read_csv(input_file_path)
    is_numeric = pd.api.types.is_numeric_dtype(df[aggregation_column])
    if is_numeric:
        aggregation_functions = {
            'mean': df[aggregation_column].mean(),
            'median': df[aggregation_column].median(),
            'mode': df[aggregation_column].mode().iloc[0],
            'sum': df[aggregation_column].sum(),
            'count': df[aggregation_column].count(),
        }
        if aggregation_operation in aggregation_functions:
            aggregation_result = aggregation_functions[aggregation_operation]
        else:
            raise ValueError(f"Unsupported numeric aggregation operation: {aggregation_operation}")
    else:
        if aggregation_operation == 'count':
            aggregation_result = df[aggregation_column].count()
        else:
            raise ValueError(f"Unsupported non-numeric aggregation operation: {aggregation_operation}")

    result_df = pd.DataFrame({aggregation_column: [aggregation_result]})
    result_df.to_csv(output_file, index=False)

input_file_path = '/home/harika/wikidata/data.csv'
output_folder = '/home/harika/wikidata/structured_dag'
filter_column = 'price' 
filter_operation = '<' 
filter_value = '500' 
sort_column = 'book'
aggregation_column='price'
aggregation_operation='mean'

filtered_data_task = PythonOperator(
    task_id='filtered_data_task',
    python_callable=filtered_data,
    op_kwargs={
        'input_file_path': input_file_path,
        'output_file': f'{output_folder}/filter.csv',
        'filter_column': filter_column,
        'filter_operation': filter_operation,
        'filter_value': filter_value,
    },
    dag=dag
)
sorted_data_task = PythonOperator(
    task_id='sorted_data_task',
    python_callable=sorted_data,
    provide_context=True,
    op_kwargs={
        'input_file_path': "{{ task_instance.xcom_pull(task_ids='filtered_data_task', key='output_file') }}",
        'output_file': f'{output_folder}/sort.csv',
        'sort_column': sort_column
    },
    dag=dag
)
aggregate_data_task = PythonOperator(
    task_id='aggregate_data_task',
    python_callable=aggregate_data,
    provide_context=True,
    op_kwargs={
        'input_file_path': f"{{{{ task_instance.xcom_pull(task_ids='sorted_data_task', key='output_file') }}}}",
        'output_file': f'{output_folder}/aggregation.csv',
        'aggregation_column': aggregation_column,  
        'aggregation_operation': aggregation_operation
    },
    dag=dag
)

start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

start >> filtered_data_task >> sorted_data_task >> aggregate_data_task >> end