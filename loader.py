from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
import telebot

storage = StateMemoryStorage()
bot = telebot.TeleBot(token=config.BOT_TOKEN, state_storage=storage)

