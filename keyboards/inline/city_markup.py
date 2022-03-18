from rapidapi import find_city_id
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def city_markup(name_city: str) -> InlineKeyboardMarkup:
    """Вызывает функцию find_city_id и возвращает клавиатуру с кнопками содержащими найденные варианты по запросу"""
    cities = find_city_id(name_city)
    destinations = InlineKeyboardMarkup()
    if cities:
        for city in cities:
            destinations.add(InlineKeyboardButton(text=city['city_name'],
                                                  callback_data=city['destination_id']))
        return destinations
    else:
        return None
