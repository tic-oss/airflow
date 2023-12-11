from airflow import DAG
from datetime import datetime,timedelta
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
# psycopg2 is a popular Python adapter for PostgreSQL, allowing you to connect to and interact with PostgreSQL databases from Python code
from psycopg2.extras import execute_values

default_args = {
    "owner": "Airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2023,11,20)
}

dag = DAG('hooks_test', default_args=default_args, schedule_interval='@daily')

def transfer_function(ds, **kwargs):
    query_source = "SELECT * FROM airflow.public.siva;"
    create_table_destination = "CREATE TABLE IF NOT EXISTS airflow.public.target(city_name VARCHAR(50), city_code VARCHAR(20));"
    
    # Source database connection
    source_hook = PostgresHook(postgres_conn_id='postgres_conn', schema='airflow')
    source_conn = source_hook.get_conn()
    source_cursor = source_conn.cursor()
    # Destination database connection
    destination_hook = PostgresHook(postgres_conn_id='postgres_conn', schema='airflow')
    destination_conn = destination_hook.get_conn()
    destination_cursor = destination_conn.cursor()

    source_cursor.execute(query_source)
    records = source_cursor.fetchall()
    destination_cursor.execute(create_table_destination)

    # Insert records into the destination
    if records:
        execute_values(destination_cursor, "INSERT INTO airflow.public.xyz VALUES %s", records)
        destination_conn.commit()

    # Close connections
    source_cursor.close()
    destination_cursor.close()
    source_conn.close()
    destination_conn.close()
    print("Data transferred successfully")


def list_tables(**kwargs):
    hook = PostgresHook(postgres_conn_id='postgres_conn', schema='airflow')
    conn = hook.get_conn()
    cursor = conn.cursor()
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    print(query)
    cursor.execute(query)
    print('query executed')
    table_names = [row[0] for row in cursor.fetchall()]
    print(table_names,"table_names")
    for table_name in table_names:
        print('###################################')
        print(table_name,"tablename")
    cursor.close()
    conn.close()

t1 = PythonOperator(task_id='transfer', python_callable=transfer_function, provide_context=True, dag=dag)   
t2 = PythonOperator(task_id='tables', python_callable=list_tables, provide_context=True, dag=dag)

t2>>t1
