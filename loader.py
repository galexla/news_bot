import sys
import loguru
import telebot
from telebot import TeleBot, logging
from telebot.storage import StateMemoryStorage

from config_data import config


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

bot_logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)
# telebot.logger.setLevel(logging.INFO)

loguru.logger.add(sys.stdout, level='DEBUG')
# loguru.logger.add('logs/error.log', level='ERROR', rotation="10 MB")
