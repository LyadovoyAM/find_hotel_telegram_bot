import requests


def get_photo(hotel_id: str, number_photo: int) -> list:
    """Функция получения ссылок на фото. Получает ID отеля и количество фотографий для вывода, отправляет запрос по
    ID отеля, обрабатывает и возвращает список из строк со ссылками на фотографии"""
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "aec92ca8abmsh7cc8ae8745bed4ap10a489jsn01b5cbbb780b"
    }

    photo_response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
    photo_response_data = photo_response.json()
    photos_url = []

    if photo_response.status_code != 204:
        try:
            for photo_num in range(number_photo):
                new_photo: str = photo_response_data['hotelImages'][photo_num].get('baseUrl')
                new_photo = new_photo.format(size=photo_response_data['hotelImages'][photo_num]['sizes'][0].get('suffix'))
                photos_url.append(new_photo)
        except (ValueError, KeyError):
            return 'фото не найдены'
        return photos_url
    else:
        return 'Ошибка запроса'


def find_hotels_lowprice(user_town: str, arrival_date: str, date_departure: str, hotel_number: str) -> list:
    """Функция реализации запроса lowprice, по поиску отелей с самой низкой ценой.
    Принимает на вход название населенного пункта, отправляет запрос для
    получения ID населенного пункта, затем направляет запрос используя ID отеля для получения названия, адреса,
    стоимости и расстояния от центра города. Возвращает список из списков с информацией по каждому отелю в виде списка
    [ID отеля, строка с информацией по отелю]."""
    url_locate = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring_locate = {"query": user_town, "locale": "en_EN", "currency": "RUB"}

    headers_locate = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "dc28012bc9msh3d7a878ec7e53bfp1b0016jsncdaa9f86a272"
        }

    response_locate = requests.request("GET", url_locate, headers=headers_locate, params=querystring_locate)

    if response_locate.status_code != 204:
        try:
            city_group = response_locate.json()['suggestions'][0]['entities']
        except ValueError:
            return 'Данные не найдены'
    else:
        return 'Ошибка запроса'

    city_id = None

    for locate in city_group:
        if locate['type'] == 'CITY':
            city_name = locate['name']
            if city_name.lower() == user_town.lower():
                city_id = locate['destinationId']

    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": hotel_number, "checkIn": arrival_date,
                   "checkOut": date_departure, "adults1": "1", "sortOrder": "PRICE", "locale": "en_EN", "currency": "RUB"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "dc28012bc9msh3d7a878ec7e53bfp1b0016jsncdaa9f86a272"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    low_price_hotels = {}
    if response.status_code != 204:
        try:
            low_price_hotels = response.json()['data']['body']['searchResults']['results']
        except (ValueError, KeyError):
            return 'Данные не найдены 2'

    messages = []

    for hotel in low_price_hotels:
        try:
            message = ''.join(['Название: ', hotel['name'], '\n', 'Адрес: ', hotel['address']['streetAddress'], '\n'])
            hotel_id = hotel['id']
            for landmark in hotel['landmarks']:
                if landmark['label'] == 'Центр города' or landmark['label'] == 'City center':
                    message = ''.join([message, 'Расстояние от центра: ', landmark['distance'], '\n'])
            message = ''.join([message, 'Цена за сутки: ', str(hotel['ratePlan']['price']['exactCurrent']), ' рублей'])
            new_message = [hotel_id, message]
            messages.append(new_message)
        except(KeyError, ValueError, IndexError):
            return 'Не удалось обработать данные'

    return messages
