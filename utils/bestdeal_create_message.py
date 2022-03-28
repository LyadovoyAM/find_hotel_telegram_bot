from loguru import logger
import re

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')


def test_center_distance(hotel_info: dict, distance_min: int, distance_max: int) -> list:
    """Функция проверки соответствия заданного пользователем расстояния от центра"""
    distance_flag = False
    city_center_distance_km = 0
    for hotel_test in hotel_info['landmarks']:
        if hotel_test['label'].lower() == 'центр города' or hotel_test['label'].lower() == 'city center':
            city_center_distance_1 = re.sub(',', '.', hotel_test['distance'])
            city_center_distance_2 = re.sub(r'[^.\d]', '', city_center_distance_1)
            city_center_distance_ml = float(city_center_distance_2)
            city_center_distance_km = round(1.60934 * city_center_distance_ml, 1)
            if distance_min <= city_center_distance_km <= distance_max:
                distance_flag = True
    return [distance_flag, city_center_distance_km]


@logger.catch
def make_bestdeal_message(results: dict, hotel_number: int, distance_min: int, distance_max: int, number_days: int) -> list:
    """Проходит по словарю и собирает строку с информацией об отеле, ID отеля и объединяет их в список.
        Возвращает список со списками [hotel['id'], message] по каждому отелю"""
    messages = list()
    try:
        for hotel in results['results']:
            right_hotel = test_center_distance(hotel, distance_min, distance_max)

            if right_hotel[0]:
                message = ''.join(['Название: ', hotel['name'], '\n'])

                if 'streetAddress' in hotel['address'].keys():
                    message = ''.join([message, 'Адрес: ', hotel['address']['streetAddress'], '\n'])
                else:
                    message = ''.join([message, 'Адрес: ', 'Информация с адресом отсутствует', '\n'])

                price = re.sub(',', '', hotel['ratePlan']['price']['current'])

                if 'fullyBundledPricePerStay' in hotel['ratePlan']['price'].keys():
                    find_total_price = re.search(r'\$\d+', hotel['ratePlan']['price']['fullyBundledPricePerStay'])
                    total_price = find_total_price.group()
                else:
                    number_price = int(re.sub(r'\D', '', price))
                    total_price = str(number_price * number_days)
                message = ''.join([message, 'Расстояние от центра: ',  str(right_hotel[1]), ' км', '\n',
                                   'Цена за сутки: ', price, '\n', 'Цена за весь указанный срок проживания: ',
                                   total_price, '$', '\n'])
                hotel_id = hotel['id']
                url = f'https://ru.hotels.com/ho{hotel_id}'
                message = ''.join([message, 'Ссылка на сайт: ', url, '\n'])
                messages.append([hotel_id, message])

            if len(messages) == hotel_number:
                break
        return messages

    except (KeyError, TypeError):
        return None
