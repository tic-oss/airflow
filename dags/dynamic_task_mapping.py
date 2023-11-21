from __future__ import annotations
from datetime import datetime
from airflow import DAG
from airflow.decorators import task

@task
def add_one(x: int):
        return x + 1
@task
def sum_it(values):
        total = sum(values)
        print(f"Total was {total}")

# with DAG(dag_id="dynamic_task_mapping", start_date=datetime(2023, 11, 20)) as dag:
#     added_values = add_one.expand(x=[1, 2, 3])
#     sum_it(added_values)

#--------------------------------------------------------------------------------------
@task
def make_list():
    # This can also be from an API call, checking a database, -- almost anything you like, as long as the
    # resulting list/dictionary can be stored in the current XCom backend.
    return [1, 2, {"a": "b"}, "str"]
@task
def consumer(arg):
    print(arg)
# with DAG(dag_id="task-gen-mapping", start_date=datetime(2022, 4, 2)) as dag:
#     consumer.expand(arg=make_list())

# -------------------------------------------------------------------------------------
# with DAG(dag_id="repeated_mapping", start_date=datetime(2023, 11, 20)) as dag:
    first = add_one.expand(x=[1, 2, 3]) #the values would be 2,3,4
    second = add_one.expand(x=first) #as add_one is again aplied to first now the values would be 3,4,5

@task
def add(x: int, y: int):
    return x + y

# with DAG(dag_id="adding_params", start_date=datetime(2023, 11, 20)) as dag:
#     added_values = add.partial(y=10).expand(x=[1, 2, 3])

# with DAG(dag_id="adding_multiple_params", start_date=datetime(2023, 11, 20)) as dag:
#     added_values = add.expand(x=[2, 4, 8], y=[5, 10])
