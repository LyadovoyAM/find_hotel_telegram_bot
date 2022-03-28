from loader import bot
from states.find_hotel_info import UserInfoState
from telebot.types import Message
from loguru import logger
from database.history_db import Request, HotelsInfo

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')
Request.create_table()
HotelsInfo.create_table()


@bot.message_handler(commands=['lowprice'])
@logger.catch
def lowprice(message: Message) -> None:
    """Функция обработчик команды /lowprice. Отправляет пользователю сообщение с запросом названия города."""
    bot.set_state(message.from_user.id, UserInfoState.name_city, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите название города для поиска отелей')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text
