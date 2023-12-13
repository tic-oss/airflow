from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
import pandas as pd
from datetime import datetime
import os

dag = DAG('structured_data', start_date=datetime(2023, 12, 12), description='Data Pipeline for structured data')

def filtered_data(input_file_path, output_file, filter_column, filter_value, **kwargs):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df = pd.read_csv(input_file_path)
    is_numeric = pd.api.types.is_numeric_dtype(df[filter_column])
    print('#############',is_numeric)
    if is_numeric:
        comparison_operator = filter_value[0]  
        threshold_value = float(filter_value[1:])
        print(comparison_operator,'#######',threshold_value)

        if comparison_operator == '<':
            filtered_df = df[df[filter_column] < threshold_value]
        elif comparison_operator == '>':
            filtered_df = df[df[filter_column] > threshold_value]
        elif comparison_operator == '<=':
            filtered_df = df[df[filter_column] <= threshold_value]
        elif comparison_operator == '>=':
            filtered_df = df[df[filter_column] >= threshold_value]
        elif comparison_operator in ['==','=','']:
            filtered_df = df[df[filter_column] == threshold_value]
        else:
            raise ValueError(f"Unsupported numeric comparison operator: {comparison_operator}")
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
    print('#############',is_numeric)
    if is_numeric:
        if aggregation_operation == 'mean':
            aggregation_result = df[aggregation_column].mean()
        elif aggregation_operation == 'median':
            aggregation_result = df[aggregation_column].median()
        elif aggregation_operation == 'mode':
            aggregation_result = df[aggregation_column].mode().iloc[0]  # Mode can have multiple values, so we take the first one
        elif aggregation_operation == 'sum':
            aggregation_result = df[aggregation_column].sum()
        else:
            raise ValueError(f"Unsupported numeric comparison operator: {aggregation_operation}")
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
filter_value = '<500' 
sort_column = 'book'
aggregation_column='author'
aggregation_operation='count'

filtered_data_task = PythonOperator(
    task_id='filtered_data_task',
    python_callable=filtered_data,
    op_kwargs={
        'input_file_path': input_file_path,
        'output_file': f'{output_folder}/filter.csv',
        'filter_column': filter_column,
        'filter_value': filter_value,
        'aggregation_operation': aggregation_operation
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