import os
from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    exit('No environment variables found, .env file does not exist')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
TEXT_ANALYSIS_API_KEY = os.getenv('TEXT_ANALYSIS_API_KEY')
DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справку'),
    ('summary', 'Получить краткое содержание новостей за неделю')
)
