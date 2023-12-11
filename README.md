# Airflow

Apache Airflow provides a simple way to write, schedule, and monitor workflows using pure Python. 
It works well as an orchestrator, but it’s not meant to process data. You can integrate a different tool into a pipeline, such as Apache Spark, if you need to process data.


## Prerequisites
- Python (version >= 3.10)
- Pip (to install Python packages)
- [Optional] Additional prerequisites, if any
- [Set up Airflow home directory ] ```export AIRFLOW_HOME=~/airflow```
- [Define Airflow version] ```AIRFLOW_VERSION=2.7.3```
- [Define Python version] ```PYTHON_VERSION=3.10```
- ```CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"```


## Installation
To install the project dependencies, run the following command:

```bash
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```


## Run Airflow
To run airflow locally, run the following command

```bash
airflow standalone
```

## Access Airflow UI
Visit ```localhost:8080```


After running airflow you would be asked to enter the credentials which would be 
```
username: admin
password: (it would be mentioned in standalone_admin_password.txt file in airflow directory)
```