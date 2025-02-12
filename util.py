from datetime import datetime
from typing import Any

from aiohttp import ClientSession
from geopy.geocoders import Nominatim
import re
import requests


def get_weaher(latitude: float, longitude: float, weather_token) -> Any | None:
    """Функция для получения текущенго прогноза погоды"""
    try:
        r = requests.get(f'http://api.openweathermap.org/data/2.5/weather?units=metric&lang=ru&lat={latitude}&lon={longitude}&appid={weather_token}')
        data = r.json()
        return data
    except Exception as err:
        print(err)


def get_hourly_forecast(lat: float, lon:float, weather_token) -> list | None:
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={weather_token}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        return data['list']  # Возвращает список прогнозов
    else:
        print(f"Ошибка: {data['message']}")
        return None


def get_adrr(location: list) -> str:
    """Возвращает адрес места"""
    try:
        geo_loc = Nominatim(user_agent="GetLoc")
        loc_name = geo_loc.reverse(location)
        print(location)
        return loc_name.address
    except AttributeError:
        return "Для этой точки нет адреса"


def format_msg(coord: str) -> str | None:
    """
    Форматирует координаты
    """
    try:
        str_ = coord.replace(',', '.')
        return str_
    except Exception:
        print('Не строка')


def check_format(str_: str) -> bool | None:
    """
    Проверяет формат координат
    """
    pattern = r'^-?\d{0,3}\.\d{1,8}$'
    prog = re.compile(pattern)
    try:
        result = prog.match(str_)
        if result:
            return True
        else:
            return False
    except Exception as err:
        print(err)


def wind_direction(grad: float) -> str:
    """
    Возвращает направление ветра
    """
    direction = ''
    if (0 < grad < 22.5) or (337.5 < grad < 360.0):
        direction = 'Северный'
    elif 22.5 < grad < 67.5:
        direction = 'Северо-восточный'
    elif 67.5 < grad < 112.5:
        direction = 'Восточный'
    elif 112.5 < grad < 157.5:
        direction = 'Юго-восточный'
    elif 157.5 < grad < 202.5:
        direction = 'Южный'
    elif 202.5 < grad < 247.5:
        direction = 'Юго-западный'
    elif 247.5 < grad < 292.5:
        direction = 'Западный'
    elif 295.5 < grad < 337.5:
        direction = 'Северо-западный'
    return direction


# Функция для получения координат города
async def get_coordinates(city_name: str):
    url = f'https://nominatim.openstreetmap.org/search?q={city_name}&format=json&addressdetails=1'
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data:
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                return latitude, longitude
            else:
                return None


def format_date(date_str: str) -> str:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    new_date_str = date_obj.strftime("%d %b %Y %H:%M")
    return new_date_str



# get_weather(48.744919, 44.525669, '59bdb9972b4f4e4972d35cea19ffb337')