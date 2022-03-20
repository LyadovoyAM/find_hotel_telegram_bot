from loguru import logger
from loader import bot
from telebot.types import Message
from utils.make_history_message import make_history_message


@bot.message_handler(commands=['history'])
@logger.catch
def history(message: Message) -> None:
    """Функция отлавливает команду /history. Вызывает функцию для получения информации о введенных пользователем
    запросах из базы данных и отправляет сообщение с ними."""
    messages = make_history_message(message.from_user.id)
    for text in messages:
        bot.send_message(message.from_user.id, text)
