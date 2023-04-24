import os
import sys
import requests
from loguru import logger
from telebot.types import Message

from loader import bot
from utils import get_summary


def get_news_from_file() -> str:
    directory = os.path.dirname(sys.modules['__main__'].__file__) + os.sep
    filepath = directory + 'news_text_descr.txt'
    with open(filepath, 'r') as file:
        return file.read()


@bot.message_handler(commands=['summary'])
def bot_summary(message: Message) -> None:
    """
    Handles the summary command

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    text = get_news_from_file()
    try:
        summary_text = get_summary(text)
        bot.reply_to(message, summary_text)
    except (requests.RequestException, requests.exceptions.JSONDecodeError) as exception:
        logger.exception(exception)
        # TODO: be more specific?
        bot.reply_to(
            message, 'Some error occurred. You may have entered an invalid data')
