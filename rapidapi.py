import json
import requests
from config_data.config import RAPID_API_KEY
import re
from loguru import logger
from utils.low_high_price_create_message import make_low_high_price_info_message
from utils.create_photo_url import make_photo_url
from utils.bestdeal_create_message import make_bestdeal_message
from utils.calculate_number_days import calculate_days

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')


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
    querystring_locate = {"query": user_town, "locale": "ru_RU", "currency": "USD"}
    headers_locate = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
    }
    request = request_to_api(url=url_locate,  headers=headers_locate, querystring=querystring_locate)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, request)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        cities = list()
        try:
            for city_info in suggestions['entities']:
                result_destination = re.sub(r'<.*>\S*', '', city_info['caption'])
                if result_destination.find(city_info['name']) == -1:
                    result_destination = ''.join([city_info['name'], ',', result_destination])
                cities.append({'city_name': result_destination, 'destination_id': city_info['destinationId']})
            return cities
        except KeyError:
            return None


@logger.catch
def find_hotels(city_id: str, hotel_number: str, arrival_date: str, date_departure: str, command: str) -> list:
    """Функция формирования и обработки запроса по поиску отелей. Словарь с информацией об отелях обрабатывается
    с помощью функции make_low_high_price_info_message. возвращает список со списками из ID отеля и строкой с сообщением"""
    url = "https://hotels4.p.rapidapi.com/properties/list"
    if command == '/lowprice':
        sort_order = "PRICE"
    else:
        sort_order = "PRICE_HIGHEST_FIRST"
    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": hotel_number, "checkIn": arrival_date,
                   "checkOut": date_departure, "adults1": "1", "sortOrder": sort_order, "locale": "en_EN",
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


@logger.catch
def find_hotels_bestdeal(city_id: str, hotel_number: int, arrival_date: str, date_departure: str,
                         distance_min: int, distance_max: int, price_min: str, price_max: str) -> list:
    """Функция формирования и обработки запроса по поиску отелей. Словарь с информацией об отелях обрабатывается
    с помощью функции make_bestdeal_message. возвращает список со списками из ID отеля и строкой с сообщением.
    Проверяет количество найденных результатов с количеством заданным пользователем, при необходимости отправляет повторный запрос
    со следующей страницы"""
    page_number = 1
    new_messages = []
    number_days = calculate_days(arrival_date=arrival_date, date_departure=date_departure)
    while True:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {"destinationId": city_id, "pageNumber": str(page_number), "pageSize": "25", "checkIn": arrival_date,
                       "checkOut": date_departure, "adults1": "1", "priceMin": price_min, "priceMax": price_max,
                       "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "en_EN", "currency": "USD",
                       "landmarkIds": "city center"}

        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': RAPID_API_KEY
        }
        response = request_to_api(url=url,  headers=headers, querystring=querystring)
        low_price_find = re.search(r'(?<=,)"searchResults":.+?(?=,"sortResults)', response)
        try:
            if low_price_find:
                search_results = json.loads(f"{{{low_price_find[0]}}}")
                results = search_results['searchResults']
                messages = make_bestdeal_message(results, hotel_number, distance_min, distance_max, number_days)
                new_messages.extend(messages)
            else:
                return None
            pagination = search_results['searchResults']['pagination']
            if len(new_messages) >= hotel_number or pagination.get('currentPage') == pagination.get('nextPageNumber', page_number):
                break
            else:
                page_number += 1
        except KeyError:
            return None
    return new_messages[:hotel_number]
