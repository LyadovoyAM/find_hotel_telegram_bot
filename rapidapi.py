import json
import requests
from dotenv import load_dotenv
from config_data.config import RAPID_API_KEY
import re
from loguru import logger
from utils.low_high_price_create_message import make_low_high_price_info_message
from utils.create_photo_url import make_photo_url

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')

load_dotenv()


@logger.catch
def request_to_api(url: str, headers: dict, querystring: dict) -> str:
    """Универсальная функция по отправке запроса на rapidapi. Возвращает строку."""
    try:
        response_locate = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        if response_locate.status_code == requests.codes.ok:
            return response_locate.text
        else:
            return None

    except TimeoutError:
        return None


@logger.catch
def find_city_id(user_town: str) -> list:
    """Функция формирования и обработки запроса с названием города. Возвращает список из словарей с названием найденных
    вариантов и их ID"""
    url_locate = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring_locate = {"query": user_town, "locale": "en_US", "currency": "USD"}
    headers_locate = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
    }
    request = request_to_api(url=url_locate,  headers=headers_locate, querystring=querystring_locate)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, request)
    if find:
        # TODO Не совсем понял как работает f"{{{find[0]}}}" с json.loads. Сам информацию к сожалению не нашел.
        suggestions = json.loads(f"{{{find[0]}}}")
        cities = list()
        try:
            for city_info in suggestions['entities']:
                result_destination = re.sub(r'<.*>\S*', '', city_info['caption'])
                if result_destination.find(city_info['name']) == -1:
                    result_destination = ''.join([city_info['name'], ',', result_destination])
                cities.append({'city_name': result_destination, 'destination_id': city_info['destinationId']})
            return cities
# TODO Везде где обрабатываю запрос по ключам поставил проверку на KeyError, хотя есть проверка через регулярные выражения,
#  мне пока эта ошибка не выпадала. Стоит ли оставить или может убрать

        except KeyError:
            return None


@logger.catch
def find_hotels(city_id: str, hotel_number: str, arrival_date: str, date_departure: str) -> list:
    """Функция формирования и обработки запроса по поиску отелей. Словарь с информацией об отелях обрабатывается
    с помощью функции make_low_high_price_info_message. возвращает список со списками из ID отеля и строкой с сообщением"""
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": hotel_number, "checkIn": arrival_date,
                   "checkOut": date_departure, "adults1": "1", "sortOrder": "PRICE", "locale": "en_EN",
                   "currency": "USD"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
    }
    response = request_to_api(url=url,  headers=headers, querystring=querystring)
    low_price_find = re.search(r'(?<=,)"results":.+?(?=,"pagination)', response)
    if low_price_find:
        results = json.loads(f"{{{low_price_find[0]}}}")
        new_messages = make_low_high_price_info_message(results)
        return new_messages
    else:
        return None


@logger.catch
def find_photo_url(hotel_id: str, photo_number: int) -> list:
    """Функция формирования и обработки запроса для получения ссылок на фотографии отеля. Словарь с информацией
    о фотографиях обрабатывается с помощью функции make_photo_url. Возвращает список со ссылками на фото в количестве
    photo_number"""
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
    }

    photo_response = request_to_api(url=url,  headers=headers, querystring=querystring)
    pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages)'
    find_photo = re.search(pattern, photo_response)
    if find_photo:
        results = json.loads(f"{{{find_photo[0]}}}")
        photo_url = make_photo_url(photo_number=photo_number, photo_data=results)
        return photo_url
    else:
        return None
