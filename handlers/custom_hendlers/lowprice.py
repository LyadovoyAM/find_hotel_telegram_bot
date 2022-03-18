from loader import bot
from states.find_hotel_info import UserInfoState
from telebot.types import Message, CallbackQuery
from keyboards.inline.city_markup import city_markup
from keyboards.inline.yes_no_keyboard import yes_or_no
from loguru import logger
from rapidapi import find_hotels, find_photo_url
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime
from utils.change_language_date import change_language_date

logger.add('debug.log', format='{time} {level} {message}', level='INFO')


# TODO Некоторые функции из lowprice будут использоваться в highprice и bestdeal. Лучше универсальные функции выделить
#  в отдельный файл или можно импортировать и ссылаться на этот?


@bot.message_handler(commands=['lowprice'])
@logger.catch
def lowprice(message: Message) -> None:
    """Функция обработчик команды /lowprice. Отправляет пользователю сообщение с запросом названия города."""
    bot.set_state(message.from_user.id, UserInfoState.name_city, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите название города для поиска отелей')


@bot.message_handler(state=UserInfoState.name_city)
@logger.catch
def choice_city(message: Message) -> None:
    """Функция получения информации о названии населенного пункта. Вызывает функцию city_markup и выводит клавиатуру
     с вариантами найденными на rapidapi. Сохраняет информацию о введенном населенном пункте пользователем в виде строки
     в словарь c ключом 'name_city'."""
    new_markup = city_markup(message.text)
    if new_markup is not None:
        bot.send_message(message.from_user.id, 'Выберите ваш вариант, пожалуйста:',
                         reply_markup=new_markup)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name_city'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Про запросе города возникла ошибка, попробуйте ввести город еще раз.')


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
@logger.catch
def callback_choice_city(call: CallbackQuery) -> None:
    """Функция получения информации о выбранном пользователем на клавиатуре городе. Сохраняет ID города в словарь
    с ключом 'city_id'. Создает календарь для выбора даты заезда в отель. Отправляет запрос с выбором года."""
    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=datetime.date.today()).build()
    text = change_language_date(f"Выберите дату заезда. \nВведите {LSTEP[step]}")
    bot.send_message(call.message.chat.id,
                     text,
                     reply_markup=calendar)
    bot.set_state(call.message.chat.id, UserInfoState.number_hotels)
    # TODO когда функция принимает на вход CallbackQuery, а не Message, ссылка на call.massage.from_user_id выдает ошибку
    #  пришлось ссылаться только на call.message.chat.id в методах set_state, retrieve_data и send_message. Все работает,
    #  но есть сомнения, что так стоит делать
    with bot.retrieve_data(call.message.chat.id) as data:
        data['city_id'] = call.data


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
@logger.catch
def callback_date_arrival(call: CallbackQuery) -> None:
    """Функция продолжает собирать информацию дате заезда. Запрашивает месяц и день заезда. Сохраняет информацию
    о дате выезда в словарь с ключом 'arrival_date'.
    Создает второй календарь для запроса даты выезда. Отправляет запрос о годе выезда на клавиатуре"""
    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=datetime.date.today()).process(call.data)
    if not result and key:
        text = change_language_date(f"Введите {LSTEP[step]}")
        bot.edit_message_text(text,
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:

        bot.edit_message_text(f"Вы выбрали дату заезда: {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.message.chat.id) as data:
            data['arrival_date'] = str(result)
            data['min_date_departure'] = result
        calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=result).build()
        text_2 = change_language_date(f"Выберите дату выезда. \nВведите {LSTEP[step]}")
        bot.send_message(call.message.chat.id,
                         text_2,
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
@logger.catch
def callback_date_departure(call: CallbackQuery) -> None:
    """Функция продолжает собирать информацию дате выезда. Запрашивает месяц и день выезда. Сохраняет информацию
    о дате выезда в словарь с ключом 'date_departure'. Отправляет сообщение с запросом количества отелей."""

    with bot.retrieve_data(call.message.chat.id) as data_1:
        arrival_date = data_1['min_date_departure']
    result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=arrival_date).process(call.data)
    if not result and key:
        text = change_language_date(f"Введите {LSTEP[step]}")
        bot.edit_message_text(text,
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали дату выезда: {result} \n"
                              f"Введите количество отелей(не больше 25)",
                              call.message.chat.id,
                              call.message.message_id)

        with bot.retrieve_data(call.message.chat.id) as data:
            data['date_departure'] = str(result)


@bot.message_handler(state=UserInfoState.number_hotels)
@logger.catch
def get_number_hotels(message: Message) -> None:
    """Функция принимает сообщение с количеством отелей и сохраняет в словарь с ключом 'number_hotels'.
    Отправляет запрос в виде клавиатуры о необходимости вывода фото."""
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Желаете вывести фото?', reply_markup=yes_or_no())
        bot.set_state(message.from_user.id, UserInfoState.photo_flag, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_hotels'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Сообщение должно содержать только цифры')


@bot.callback_query_handler(func=lambda call: call.data.isalpha())
@logger.catch
def get_photo_flag(call: CallbackQuery) -> None:
    """Функция принимает информацию о необходимости вывода фотографий и сохраняет в словарь с ключом 'photo_flag'
    True либо False. При необходимости вывода отправляет сообщение с запросом количества фотографий, в обратном случает
    вызывает функцию send_hotel_info"""
    if call.data == 'yes':
        bot.send_message(call.message.chat.id, 'Укажите количество фотографий(максимум 25)')
        bot.set_state(call.message.chat.id, UserInfoState.number_photos)
        with bot.retrieve_data(call.message.chat.id) as data:
            data['photo_flag'] = True
    elif call.data == 'no':
        with bot.retrieve_data(call.message.chat.id) as data_1:
            data_1['photo_flag'] = False
            data_1['number_photos'] = 0
        send_hotels_info(call.message)


@bot.message_handler(state=UserInfoState.number_photos)
@logger.catch
def get_number_photos(message: Message) -> None:
    """Функция принимает сообщение о количестве фотографий и сохраняет в словарь с ключом 'number_photos', затем
    вызывает функцию send_hotel_info"""
    if message.text.isdigit():
        if int(message.text) <= 25:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['number_photos'] = int(message.text)
            send_hotels_info(message)
        else:
            bot.send_message(message.from_user.id, 'Число должно быть не больше 25')
    else:
        bot.send_message(message.from_user.id, 'Сообщение должно содержать только цифры')


@logger.catch
def send_hotels_info(message: Message) -> None:
    """Функция отправки сообщений с информацией об отелях. Вызывает функцию find_hotels из файла rapidapi.py
    для получения информации по отелям. Из полученного списка с помощью цикла проходится по элементам и отправляет
    сообщение, при необходимости вызывает функцию get_photo из файла rapidapi.py и отправляет фотографии."""
    with bot.retrieve_data(message.chat.id) as data:
        new_massages = find_hotels(city_id=data['city_id'],
                                   arrival_date=data['arrival_date'],
                                   date_departure=data['date_departure'],
                                   hotel_number=data['number_hotels'])
        get_photo = data['photo_flag']
        number_photo = data['number_photos']
    if new_massages is not None:
        # TODO Во всех функциях где стоят проверки try-except и if-else в случае некорректного вывода возвращаю None,
        #  а перед выводом сообщения проверяю на not None. Это нормальное решение или есть вариант "поизящнее"
        for new_massage in new_massages:
            bot.send_message(message.chat.id, new_massage[1])
            if get_photo:
                photo_paths = find_photo_url(hotel_id=new_massage[0], photo_number=number_photo)
                for photo_path in photo_paths:
                    bot.send_photo(message.chat.id, photo_path)
    else:
        bot.send_message(message.from_user.id, 'По вашему запросу ни чего не найдено. '
                                               'Для повторного поиска введите еще раз /lowprice')
    bot.delete_state(message.chat.id)
