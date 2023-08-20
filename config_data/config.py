import logging
import os

from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    exit('No environment variables found, .env file does not exist')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DROP_TABLES = os.getenv('DROP_TABLES', 'False').lower() == 'true'

loguru_levels = set('TRACE DEBUG INFO SUCCESS WARNING ERROR CRITICAL'.split())
LOG_LEVEL_APP = os.getenv('LOG_LEVEL_APP', 'INFO').upper()
LOG_LEVEL_APP = LOG_LEVEL_APP if LOG_LEVEL_APP in loguru_levels else 'INFO'

logging_levels = set('NOTSET DEBUG INFO WARNING ERROR CRITICAL'.split())
LOG_LEVEL_BOT = os.getenv('LOG_LEVEL_BOT', 'INFO').upper()
LOG_LEVEL_BOT = (
    getattr(logging, LOG_LEVEL_BOT)
    if LOG_LEVEL_BOT in logging_levels
    else logging.INFO
)


NEWS_ID = 'id'
NEWS_TITLE = 'title'
NEWS_DESCRIPTION = 'description'
NEWS_BODY = 'content'
NEWS_URL = 'url'

DEFAULT_COMMANDS = (
    ('start', 'Start bot'),
    ('help', 'Display help'),
    ('news', 'Get news in 1 week: summary and top 5 news'),
    ('history', 'Get search queries history'),
)
