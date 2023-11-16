import logging

from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults

log = logging.getLogger(__name__)

class MyFirstOperator(BaseOperator):

# The @apply_defaults decorator is used to apply default values to the operator's parameters.
# the __init__ function can be used to configure settings for the task and
# a method named execute is called when the task instance is executed.

    @apply_defaults
    def __init__(self, my_operator_param, *args, **kwargs):
        self.operator_param = my_operator_param
        super(MyFirstOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        log.info("Hello World!")
        log.info('operator_param: %s', self.operator_param)


#--------------------------------------------------------------------------------------
# from datetime import datetime
# from airflow.operators.sensors import BaseSensorOperator

# class MyFirstSensor(BaseSensorOperator):

#     @apply_defaults
#     def __init__(self, *args, **kwargs):
#         super(MyFirstSensor, self).__init__(*args, **kwargs)

#     def poke(self, context):
#         current_minute = datetime.now().minute
#         if current_minute % 3 != 0:
#             log.info("Current minute (%s) not is divisible by 3, sensor will retry.", current_minute)
#             return False

#         log.info("Current minute (%s) is divisible by 3, sensor finishing.", current_minute)
#         return True
#------------------------------------------------------------------------------------


class MyFirstPlugin(AirflowPlugin):
    name = "my_first_plugin"
    operators = [MyFirstOperator]#, MyFirstSensor]

# The operators attribute is a list that contains the custom operators associated with your plugin