import sys

import loguru
import redis
import telebot
from telebot import TeleBot, logging
from telebot.storage import StateRedisStorage

from config_data import config

storage = StateRedisStorage(host=config.REDIS_HOST, port=config.REDIS_PORT,
                            db=config.REDIS_DB, password=config.REDIS_PASSWORD)
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

redis_connection = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                               db=config.REDIS_DB, password=config.REDIS_PASSWORD,
                               decode_responses=True, encoding='utf-8',
                               socket_timeout=None, health_check_interval=10)

bot_logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)
telebot.logger.setLevel(logging.INFO)

loguru.logger.add(sys.stdout, level='DEBUG')
# loguru.logger.add(sys.stdout, level='INFO')
# loguru.logger.add('logs/error.log', level='ERROR', rotation="10 MB")
