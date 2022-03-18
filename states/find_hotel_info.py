from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    name_city = State()
    choice_city = State()
    number_hotels = State()
    photo_flag = State()
    number_photos = State()

