import telebot
import lowprice_rapidapi


bot = telebot.TeleBot('5184010735:AAGV_JfRbwfFKpdYKmTh7-wcKZPqK_MbS-4')

hotel_info = dict()


@bot.message_handler(commands=['start'])
def start_message(message: telebot.types.Message) -> None:
    """Функция бота. При получении сообщения /start отправляет сообщение для выбора необходимой функции."""
    bot.send_message(message.chat.id, 'Выберите необходимую функцию: \n /lowprice \n /highprice \n /bestdeal \n /history')


@bot.message_handler(content_types=['text'])
def low_price(message: telebot.types.Message) -> None:
    """Функция команды /lowprice. При получении сообщения /lowprice начинает процесс сбора информации об отеле для запроса"""
    if message.text == '/lowprice':
        bot.send_message(message.from_user.id, 'Введите название города')
        bot.register_next_step_handler(message, name_town_setter)


def name_town_setter(message: telebot.types.Message) -> None:
    """Функция получения информации о названии населенного пункта. Сохраняет информацию в виде строки в словарь Hotel info
     c ключом 'name_town'. Отправляет сообщение о выборе даты заезда."""
    hotel_info['name_town'] = message.text
    bot.send_message(message.from_user.id, 'Введите дату заезда(YYYY-MM-DD)')
    bot.register_next_step_handler(message, arrival_date_setter)


def arrival_date_setter(message: telebot.types.Message) -> None:
    """Функция получения информации о выборе даты заезда. Сохраняет информацию в виде строки в словарь Hotel info
    c ключом 'arrival_date'. Отправляет сообщение о выборе даты выезда."""
    hotel_info['arrival_date'] = message.text
    bot.send_message(message.from_user.id, 'Введите дату выезда(YYYY-MM-DD)')
    bot.register_next_step_handler(message, date_departure_setter)


def date_departure_setter(message: telebot.types.Message) -> None:
    """Функция получения информации о выборе даты выезда. Сохраняет информацию в виде строки в словарь Hotel info
    c ключом 'date_departure'. Отправляет сообщение о выборе количества отелей для поиска."""
    hotel_info['date_departure'] = message.text
    bot.send_message(message.from_user.id, 'Введите количество отелей(не больше 25)')
    bot.register_next_step_handler(message, hotel_number_setter)


def hotel_number_setter(message: telebot.types.Message) -> None:
    """Функция получения информации о количестве отелей. Сохраняет информацию в виде строки в словарь Hotel info
    c ключом 'hotel_number'. Отправляет сообщение с запросом необходимости вывода фото отеля."""
    hotel_info['hotel_number'] = message.text
    bot.send_message(message.from_user.id, 'Желаете вывести фото? (да/нет)')
    bot.register_next_step_handler(message, hotel_photo_setter)


def hotel_photo_setter(message: telebot.types.Message) -> None:
    """Функция получения информации о необходимости вывода фотографий. Сохраняет значение True, если вывод требуется
     и False, если не требуется, в словарь Hotel info c ключом 'hotel_number'. Если вывод требуется запрашивает
     количество фотографий для вывода. В противном случае вызывает функцию отправки сообщения с информацией об отелях"""
    if message.text.lower() == 'да':
        hotel_info['get_photo'] = True
        bot.send_message(message.from_user.id, 'Укажите количество фотографий(максимум 25)')
        bot.register_next_step_handler(message, get_number_photo)

    elif message.text.lower() == 'нет':
        hotel_info['get_photo'] = False
        hotel_info['number_photo'] = 0
        send_hotels_info(message)


def get_number_photo(message: telebot.types.Message) -> None:
    """Функция получения информации о количестве фотографий. Сохраняет информацию в виде INT в словарь Hotel info
        c ключом 'number_photo'. Вызывает функцию отправки сообщения с информацией об отелях."""
    if message.text.isdigit():
        number_photo = int(message.text)
        if 0 < number_photo <= 25:
            hotel_info['number_photo'] = number_photo
            send_hotels_info(message)


@bot.message_handler(content_types=['text'])
def send_hotels_info(message: telebot.types.Message) -> None:
    """Функция отправки сообщений с информацией об отелях. Вызывает функцию find_hotels_lowprice из файла lowprice_rapidapi.py
    для получения информации по отелям. Из полученного списка с помощью цикла проходится по элементам и отправляет
    сообщение, при необходимости вызывает функцию get_photo из файла lowprice_rapidapi.py и отправляет фотографии."""
    new_massages = lowprice_rapidapi.find_hotels_lowprice(user_town=hotel_info['name_town'],
                                                          arrival_date=hotel_info['arrival_date'],
                                                          date_departure=hotel_info['date_departure'],
                                                          hotel_number=hotel_info['hotel_number'])

    if type(new_massages) is str:
        bot.send_message(message.from_user.id, new_massages)

    elif len(new_massages) > 0:
        for new_massage in new_massages:
            bot.send_message(message.from_user.id, new_massage[1])
            if hotel_info['get_photo']:
                photo_paths = lowprice_rapidapi.get_photo(new_massage[0], hotel_info['number_photo'])
                for photo_path in photo_paths:
                    bot.send_photo(message.from_user.id, photo_path)

    else:
        bot.send_message(message.from_user.id, 'По вашему запросу ни чего не найдено. '
                                               'Для повторного поиска введите еще раз /lowprice')


bot.polling(none_stop=True, interval=0)
