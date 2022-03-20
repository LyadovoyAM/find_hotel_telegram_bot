from peewee import *
import datetime

db = SqliteDatabase('find_hotel_history.db')


class Request(Model):
    """Класс для создания таблицы в базе данных с информацией о ID пользователя который вводил запрос, команде,
    населенном пункте, дате и времени запроса."""
    user_id = CharField()
    command = CharField()
    city = CharField()
    date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class HotelsInfo(Model):
    """Класс для создания таблицы в базе данных с текстом сообщения и ID запроса связанного с таблицей Request"""
    request_id = ForeignKeyField(Request, related_name='request')
    text_message = CharField()

    class Meta:
        database = db
