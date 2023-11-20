from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import logging as log
from airflow.sensors.base import BaseSensorOperator
# from airflow.contrib.hooks import FSHook
from airflow.hooks.filesystem import FSHook
import os
from airflow.hooks.base import BaseHook
# sudo apt-get install build-essential libmysqlclient-dev pkg-config
# pip install apache-airflow-providers-mysql
# https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.hooks.postgres_hook import PostgresHook

class DataTransferOperator(BaseOperator):
    @apply_defaults #define default arguments for a function
    def __init__(self, source_file_path, dest_file_path, delete_list, *args, **kwargs): #constructor
        #assigns the value of the source_file_path parameter to an instance variable self.source_file_path. This allows the class to store and access the source file path throughout its methods.
        self.source_file_path = source_file_path
        self.dest_file_path = dest_file_path
        self.delete_list = delete_list
        # calls the constructor of the parent class BaseOperator by using the super() function. It passes any additional arguments and keyword arguments (*args and **kwargs) to the parent class constructor.
        # *args - allows the user to pass a multiple number of arguments to the function
        # **kwargs allows us to pass a variable number of keyworded arguments to the function. Python *kwargs allows only Keyword Arguments.
        super().__init__(*args, **kwargs)

    def execute(self, context):
        SourceFile = self.source_file_path
        DestinationFile = self.dest_file_path
        DeleteList = self.delete_list

        log.info("### custom operator execution starts")
        log.info("source_file_path: %s",SourceFile)
        log.info("dest_file_path: %s",DestinationFile)
        log.info("delete_list: %s",DeleteList)

        fin = open(SourceFile)
        fout = open(DestinationFile,"a")
        for line in fin:
            log.info("reading line: %s", line)
            for word in DeleteList:
                log.info("matching string: %s", word)
                line = line.replace(word, "")
            log.info("output line is: %s", line)
            fout.write(line)
        fin.close()
        fout.close()

class FileCountSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(self, dir_path, conn_id, *args, **kwargs):
        self.dir_path = dir_path
        self.conn_id = conn_id
        super().__init__(*args, **kwargs)

    def poke(self, context):
        # setting connection with FSHook
        hook = FSHook(self.conn_id)
        basepath = hook.get_path()
        full_path = os.path.join(basepath, self.dir_path)
        self.log.info('poking location is %s', full_path)
        try:
            for root, dirs, files in os.walk(full_path):
                if len(files) >= 5:
                    return True
        except OSError:
            return False
        return False

class MySQLToPostgresHook(BaseHook):
    def __init__(self):
        print('#custom hook')

    def copy_table(self, mysql_conn, postgres_conn):
        print('fetching records from MYSQL table')
        mysqlserver = MySqlHook(mysql_conn_id='mysql_conn', schema='airflow')
        sql_query = "SELECT * from airflow.source; "
        
        source_conn = mysqlserver.get_conn()
        source_cursor = source_conn.cursor()
        source_cursor.execute(sql_query)

        data = mysqlserver.get_records(sql_query)

        print("inserting into POSTGRES table")
        postgresserver = PostgresHook(postgres_conn_id='postgres_conn', schema='airflow')
        destination_conn =  postgresserver.get_conn()

        destination_cursor = destination_conn.cursor()
        postgres_query = "INSERT INTO airflow.public.target VALUES(%s, %s);"
        for row in data:
            destination_cursor.execute(postgres_query, row)

        destination_conn.commit()       
        source_cursor.close()
        destination_cursor.close()
        source_conn.close()
        destination_conn.close()        

class DemoPlugin(AirflowPlugin):
    name ="demo_plugin"
    operators = [DataTransferOperator]
    sensors = [FileCountSensor]
    hooks = [MySQLToPostgresHook]