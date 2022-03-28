from loguru import logger
from loader import bot
from telebot.types import Message
from states.find_hotel_info import UserInfoState
from . import send_hotels_info_message
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')


@bot.message_handler(commands=['bestdeal'])
@logger.catch
def bestdeal(message: Message):
    """Функция обрабатывает команду bestdeal. Отправляет сообщение с запросом названия города"""
    bot.set_state(message.from_user.id, UserInfoState.name_city, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите название города для поиска отелей')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text


@bot.message_handler(state=UserInfoState.distance_min)
@logger.catch
def get_distance_min(message: Message) -> None:
    """Принимает минимальное расстояние от центра и отправляет запрос о максимальном расстоянии"""
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите максимальное расстояние от центра(км)')
        bot.set_state(message.from_user.id, UserInfoState.distance_max, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['distance_min'] = int(message.text)
    else:
        bot.send_message(message.from_user.id, 'Сообщение должно содержать только цифры')


@bot.message_handler(state=UserInfoState.distance_max)
@logger.catch
def get_distance_min(message: Message) -> None:
    """Принимает максимальное расстояние от центра и отправляет запрос о минимальной стоимости"""
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите минимальную стоимость в USD')
        bot.set_state(message.from_user.id, UserInfoState.price_min, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['distance_max'] = int(message.text)
    else:
        bot.send_message(message.from_user.id, 'Сообщение должно содержать только цифры')


@bot.message_handler(state=UserInfoState.price_min)
@logger.catch
def get_price_min(message: Message) -> None:
    """Принимает минимальную стоимость и отправляет запрос о максимальной стоимости"""
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите максимальную стоимость в USD')
        bot.set_state(message.from_user.id, UserInfoState.price_max, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_min'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Сообщение должно содержать только цифры')


@bot.message_handler(state=UserInfoState.price_max)
@logger.catch
def get_price_max(message: Message) -> None:
    """Принимает максимальную стоимость и вызывает функцию отправки сообщений send_hotels_info"""
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_max'] = message.text
        send_hotels_info_message.send_hotels_info(message)
    else:
        bot.send_message(message.from_user.id, 'Сообщение должно содержать только цифры')
