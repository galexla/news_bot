import requests
from loguru import logger
from telebot.types import Message

from loader import bot
from utils import get_news


@bot.message_handler(commands=['news'])
def bot_summary(message: Message) -> None:
    """
    Handles the /news command

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    try:
        get_news('Russia', '2023-04-03T00:00:00', '2023-04-09T23:59:59')
        bot.reply_to(message, 'Got news')
    except (requests.RequestException, requests.exceptions.JSONDecodeError,
            ValueError) as exception:
        logger.exception(exception)
        bot.reply_to(
            message, 'Some error occurred. You may have entered an invalid data')
