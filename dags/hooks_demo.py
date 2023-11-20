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
    "start_date": datetime(2023,11,17)
}

dag = DAG('hooks_demo', default_args=default_args, schedule_interval='@daily')

def transfer_function(ds, **kwargs):
    query = "select * from airflow.public.source_city_table"
    source_hook = PostgresHook(postgres_conn_id='postgres_conn', schema='airflow')
    source_conn = source_hook.get_conn()
    destination_hook = PostgresHook(postgres_conn_id='postgres_conn', schema='airflow')
    destination_conn = destination_hook.get_conn()
    
    # cursor - allows py code to execute postgres sql command in databse session
    # also helps in maintaining connection on database and will read results of query few rows at a time aaa
    source_cursor = source_conn.cursor()
    destination_cursor = destination_conn.cursor()
    # source_cursor.execute(insert_query)
    source_cursor.execute(query)
    records = source_cursor.fetchall()

    if records:
        print(source_cursor)
        print("records",records)
        execute_values(destination_cursor, "insert into airflow.public.target_city_table values %s", records)
        destination_conn.commit()
    
    source_cursor.close()
    destination_cursor.close()
    source_conn.close()
    destination_conn.close()
    print("Data transferred successfully")

def list_tables(**kwargs):
    # Create a PostgreSQL connection hook
    hook = PostgresHook(postgres_conn_id='postgres_conn', schema='airflow')
    conn = hook.get_conn()
    
    # Create a cursor to execute SQL queries
    cursor = conn.cursor()
    
    # SQL query to retrieve a list of table names in the current schema
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    print(query)
    # Execute the query
    cursor.execute(query)
    print('query executed')
    # Fetch all the table names
    table_names = [row[0] for row in cursor.fetchall()]
    print(table_names,"table_names")
    # Print the table names
    for table_name in table_names:
        print('###################################')
        print(table_name,"tablename")
    
    # Close the cursor and the connection
    cursor.close()
    conn.close()

t1 = PythonOperator(task_id='transfer', python_callable=transfer_function, provide_context=True, dag=dag)   
t2 = PythonOperator(task_id='tables', python_callable=list_tables, provide_context=True, dag=dag)
t2>>t1
# create table source_city_table(city_name varchar (50), city_code varchar (20));
# insert into source_city_table (city_name, city_code) values('Neew york', 'ny'), ('Los Angles', 'ls'), ('Houston', 'ht');
# update source_city_tableset city_name='New York' where city_name = 'Neew york'
# insert into source_city_table (city_name, city_code) values('Chicago', 'cg');
# select * from source_city_table
# \conninfo
# alter user postgres password 'abc';
# \p
# sudo service postgresql restart
# create schema airflow;
#  CREATE TABLE airflow.source_city_table AS SELECT * FROM public.source_city_table;
# SELECT * FROM airflow.source_city_table;

# sudo -u postgres psql
# \dt
# select * from public.source_city_table
# select * from airflow.source_city_table