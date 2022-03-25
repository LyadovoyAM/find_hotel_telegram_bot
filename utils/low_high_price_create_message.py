from loguru import logger
import re

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')


@logger.catch
def make_low_high_price_info_message(results: dict) -> list:
    """Проходит по словарю и собирает строку с информацией об отеле, ID отеля и объединяет их в список.
    Возвращает список со списками [hotel['id'], message] по каждому отелю"""
    messages = list()
    try:
        for hotel in results['results']:
            city_center_distance = 'Не удалось определить'
            message = ''.join(['Название: ', hotel['name'], '\n'])
            if 'streetAddress' in hotel['address'].keys():
                message = ''.join([message, 'Адрес: ', hotel['address']['streetAddress'], '\n'])
            else:
                message = ''.join([message, 'Адрес: ', 'Информация с адресом отсутствует', '\n'])
            for landmark in hotel['landmarks']:
                if landmark['label'].lower() == 'центр города' or landmark['label'].lower() == 'city center':
                    city_center_distance = landmark['distance']
            price = re.sub(',', '', hotel['ratePlan']['price']['current'])
            total_price = re.search(r'\$\d+', hotel['ratePlan']['price']['fullyBundledPricePerStay'])
            message = ''.join([message, 'Расстояние от центра: ', city_center_distance, '\n',
                               'Цена за сутки: ', price, '\n', 'Цена за весь указанный срок проживания: ',
                               total_price.group(), '\n'])

            hotel_id = hotel['id']
            url = f'https://ru.hotels.com/ho{hotel_id}'
            message = ''.join([message, 'Ссылка на сайт: ', url, '\n'])

            messages.append([hotel_id, message])
        return messages
    except (KeyError, TypeError):
        return None
