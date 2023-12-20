# import pandas as pd
# from datetime import datetime, timedelta

# def load_data_from_file(file_path, date):
#     try:
#         data = pd.read_csv(file_path)
#         return data
#     except FileNotFoundError:
#         print(f"File not found: {file_path}")
#     except pd.errors.EmptyDataError:
#         print(f"Empty file: {file_path}")
#     except pd.errors.ParserError:
#         print(f"Error parsing CSV file: {file_path}")
#     return None

# def predict_weather(data):
#     if data is None or data.empty:
#         return "Unknown"

#     average_temp_min = data['temp_min'].mean()
#     average_temp_max = data['temp_max'].mean()
#     return average_temp_min, average_temp_max

# def load_data_to_storage(data, storage_path):
#     if data is not None:
#         data.to_csv(storage_path, index=False)
#         print(f"Data loaded to {storage_path}")
#     else:
#         print("No data available. Not loading to storage.")

# if __name__ == "__main__":
#     tomorrow = datetime.now() + timedelta(days=1)

#     file_path = "/home/harika/Downloads/weather_data.csv"
#     weather_data = load_data_from_file(file_path, tomorrow)

#     average_temp_min, average_temp_max = predict_weather(weather_data)
    
#     print(f"The temperature in the loaded data is Minimum: {round(average_temp_min, 2)}°C, Maximum: {round(average_temp_max, 2)}°C")
#     # storage_path = "/home/harika/airflow/dags/output.csv"
#     # load_data_to_storage(predict_weather, storage_path)

from pyspark.sql import SparkSession
from datetime import datetime, timedelta

def load_data_from_file(spark, file_path):
    try:
        data = spark.read.csv(file_path, header=True, inferSchema=True)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
    return None

def predict_weather(data):
    if data is None or data.isEmpty():
        return "Unknown"

    average_temp_min = data.agg({'temp_min': 'mean'}).collect()[0][0]
    average_temp_max = data.agg({'temp_max': 'mean'}).collect()[0][0]
    return average_temp_min, average_temp_max

def load_data_to_storage(data, storage_path):
    if data is not None:
        data.write.csv(storage_path, header=True, mode='overwrite')
        print(f"Data loaded to {storage_path}")
    else:
        print("No data available. Not loading to storage.")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("WeatherPrediction").getOrCreate()

    tomorrow = datetime.now() + timedelta(days=1)

    file_path = "/home/harika/Downloads/weather_data.csv"
    weather_data = load_data_from_file(spark, file_path)

    average_temp_min, average_temp_max = predict_weather(weather_data)
    
    print(f"The temperature in the loaded data is Minimum: {round(average_temp_min, 2)}°C, Maximum: {round(average_temp_max, 2)}°C")
    
    # storage_path = "/home/harika/airflow/dags/output.csv"
    # load_data_to_storage(weather_data, storage_path)

    spark.stop()
