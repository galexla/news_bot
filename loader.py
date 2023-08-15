import os
import sys

import loguru
import redis
from telebot import TeleBot
from telebot import logger as telebot_logger
from telebot.storage import StateRedisStorage

from config_data import config
from database.init_db import create_tables, init_db

loguru.logger.add(sys.stdout, level=config.LOG_LEVEL_APP)
loguru.logger.add(os.path.join('logs', 'app.log'),
                  level=config.LOG_LEVEL_APP, rotation='30 MB')
loguru.logger.add(os.path.join('logs', 'error.log'),
                  level='ERROR', rotation='30 MB')

storage = StateRedisStorage(host=config.REDIS_HOST, port=config.REDIS_PORT,
                            db=config.REDIS_DB, password=config.REDIS_PASSWORD)

bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
telebot_logger.setLevel(config.LOG_LEVEL_BOT)

redis_connection = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                               db=config.REDIS_DB, password=config.REDIS_PASSWORD,
                               decode_responses=True, encoding='utf-8',
                               socket_timeout=None, health_check_interval=10)

init_db(config.POSTGRES_DB, host=config.POSTGRES_HOST,
        user=config.POSTGRES_USER, password=config.POSTGRES_PASSWORD,
        port=config.POSTGRES_PORT)

create_tables()
