from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
import pandas as pd
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

dag = DAG('structured_spark', start_date=datetime(2023, 12, 15), description='Data Pipeline for structured data')

def filtered_data(input_file_path, output_file, filter_column, filter_value, **kwargs):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    spark = SparkSession.builder.appName(input_file_path).getOrCreate()
    df = spark.read.csv(input_file_path, header=True, inferSchema=True)

    is_numeric = df.select((col(filter_column).cast("double").isNotNull()).alias("is_numeric")).collect()[0]["is_numeric"]
    if is_numeric:
        filtered_df = df.filter(f"{filter_column} {filter_value}")
    else:
        filtered_df = df.filter(f"{filter_column} == '{filter_value}'")

    filtered_df.write.csv(output_file, header=True, mode='overwrite')
    kwargs['ti'].xcom_push(key='output_file', value=output_file)

def sorted_data(input_file_path, output_file, sort_column, **kwargs):
    spark = SparkSession.builder.appName(input_file_path).getOrCreate()
    df = spark.read.csv(input_file_path, header=True, inferSchema=True)
    sorted_df = df.orderBy(sort_column, ascending=False)
    sorted_df.write.csv(output_file, header=True, mode='overwrite')
    kwargs['ti'].xcom_push(key='output_file', value=output_file)

def aggregate_data(input_file_path, output_file, aggregation_column, aggregation_operation):
    spark = SparkSession.builder.appName(input_file_path).getOrCreate()
    df = spark.read.csv(input_file_path, header=True, inferSchema=True)
    is_numeric = df.select((col(filter_column).cast("double").isNotNull()).alias("is_numeric")).collect()[0]["is_numeric"]
    if is_numeric:
        aggregation_result = df.agg({aggregation_column: aggregation_operation}).collect()[0][0]
    else:
        if aggregation_operation == 'count':
            aggregation_result = df[aggregation_column].count()
        else:
            raise ValueError(f"Unsupported non-numeric aggregation operation: {aggregation_operation}")

    result_df = pd.DataFrame({aggregation_column: [aggregation_result]})
    result_df.to_csv(output_file, index=False)

input_file_path = '/home/harika/wikidata/data.csv'
output_folder = '/home/harika/wikidata/structured_spark'
filter_column = 'price' 
filter_value = '>500' 
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