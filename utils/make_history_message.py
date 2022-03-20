from loguru import logger
from database.history_db import Request


@logger.catch
def make_history_message(user_id: str) -> list:
    """Функция по запросу из базы данных find_hotel_history составляет строку с информацией о запросе, далее объединяет
    сообщения в список и возвращает его"""
    messages = list()
    for request_info in Request.select().where(Request.user_id == user_id):
        message = ''.join([f'Введенная команда: {request_info.command}\n',
                           f'Дата и время запроса: {request_info.date.strftime("%Y.%m.%d, %H:%M ")}\n',
                           f'Город в запросе: {request_info.city}\n',
                           'Найденные отели: \n'])
        if request_info.request:
            for hotel_info in request_info.request:
                message = ''.join([message, '*'*30, '\n', hotel_info.text_message, '\n'])
        else:
            message = ''.join([message, '\n', 'По данному запросу ни чего не было найдено'])
        messages.append(message)
    return messages
