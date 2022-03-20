import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('token')
RAPID_API_KEY = os.getenv('rapid_api_key')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('lowprice', "Поиск отелей с низкой ценой"),
    ('history', "Вывод истории поиска отелей")
)
