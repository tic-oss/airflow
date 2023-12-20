import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = '0c9761d2ba6128cc4c00df49930dc3fd'
BASE_URL = f"https://api.openweathermap.org/data/2.5/weather?"
CITY = 'Hyderabad'

url = BASE_URL +"appid=" + API_KEY + "&q=" + CITY
response = requests.get(url).json()
temp = round(response['main']['temp'] - 275.15,2)
humidity = response['main']['humidity']
feels_like = round(response['main']['feels_like'] - 273.15,2)

print(f"Temperature : {temp} °C")
print(f"Feels like: {feels_like} °C")
print(f"Humidity: {humidity}%")
