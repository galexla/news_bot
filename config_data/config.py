import os
from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    exit('No environment variables found, .env file does not exist')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

RAPID_API_KEY = os.getenv('RAPID_API_KEY')

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

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

DEFAULT_COMMANDS = (
    ('start', 'Start bot'),
    ('help', 'Display help'),
    ('news', 'Get news in 1 week: summary and top 5 news'),
    ('history', 'Get search queries history'),
)
