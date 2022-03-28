from loguru import logger
from loader import bot
from telebot.types import Message
from states.find_hotel_info import UserInfoState


@bot.message_handler(commands=['highprice'])
@logger.catch
def highprice(message: Message):
    """Функция обработчик команды /highprice. Отправляет пользователю сообщение с запросом названия города."""
    bot.set_state(message.from_user.id, UserInfoState.name_city, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите название города для поиска отелей')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text
