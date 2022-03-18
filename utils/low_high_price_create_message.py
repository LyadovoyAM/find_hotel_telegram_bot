from loguru import logger


@logger.catch
def make_low_high_price_info_message(results: dict) -> list:
    """Проходит по словарю и собирает строку с информацией об отеле, ID отеля и объединяет их в список.
    Возвращает список со списками [hotel['id'], message] по каждому отелю"""
    messages = list()
    try:
        for hotel in results['results']:
            city_center_distance = 'Не удалось определить'
            message = ''.join(['Название: ', hotel['name'], '\n', 'Адрес: ', hotel['address']['streetAddress'], '\n'])
            for landmark in hotel['landmarks']:
                if landmark['label'].lower() == 'центр города' or landmark['label'].lower() == 'city center':
                    city_center_distance = landmark['distance']
            message = ''.join([message, 'Расстояние от центра: ', city_center_distance, '\n',
                               'Цена за сутки: ', hotel['ratePlan']['price']['current']])
            messages.append([hotel['id'], message])
        return messages
    except (KeyError, TypeError):
        return None
