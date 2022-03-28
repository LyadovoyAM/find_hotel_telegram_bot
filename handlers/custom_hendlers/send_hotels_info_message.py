from loader import bot
from loguru import logger
from telebot.types import Message
from database.history_db import HotelsInfo
from rapidapi import find_hotels_bestdeal, find_hotels, find_photo_url


@logger.catch
def send_hotels_info(message: Message) -> None:
    """Функция отправки сообщений с информацией об отелях. Вызывает функцию find_hotels или find_hotels_bestdeal из файла rapidapi.py
    для получения информации по отелям. Из полученного списка с помощью цикла проходится по элементам и отправляет
    сообщение, при необходимости вызывает функцию get_photo из файла rapidapi.py и отправляет фотографии."""
    with bot.retrieve_data(message.chat.id) as data:
        if data['command'] == '/bestdeal':
            new_massages = find_hotels_bestdeal(city_id=data['city_id'],
                                                arrival_date=data['arrival_date'],
                                                date_departure=data['date_departure'],
                                                hotel_number=int(data['number_hotels']),
                                                distance_min=data['distance_min'],
                                                distance_max=data['distance_max'],
                                                price_min=data['price_min'],
                                                price_max=data['price_max'])

        else:
            new_massages = find_hotels(city_id=data['city_id'],
                                       arrival_date=data['arrival_date'],
                                       date_departure=data['date_departure'],
                                       hotel_number=data['number_hotels'],
                                       command=data['command'])
        get_photo = data['photo_flag']
        number_photo = data['number_photos']
    if new_massages is not None and len(new_massages) > 0:
        for new_massage in new_massages:
            bot.send_message(message.chat.id, new_massage[1])
            HotelsInfo.create(request_id=data['request'], text_message=new_massage[1])
            if get_photo:
                photo_paths = find_photo_url(hotel_id=new_massage[0], photo_number=number_photo)
                for photo_path in photo_paths:
                    bot.send_photo(message.chat.id, photo_path)
    else:
        bot.send_message(message.chat.id, 'По вашему запросу ни чего не найдено. '
                         'Попробуйте еще раз')
    bot.delete_state(message.chat.id)
