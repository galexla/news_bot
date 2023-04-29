import time
import requests
from loguru import logger
from telebot.types import Message

from loader import bot
from utils import get_news
from utils.misc import get_json_value


@bot.message_handler(commands=['news'])
def bot_summary(message: Message) -> None:
    """
    Handles the /news command

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    try:
        t1 = time.time_ns()
        news = get_news('Russia', 1, 50, '2023-04-03T00:00:00', '2023-04-09T23:59:59')
        time.sleep(0.1)
        news = get_news('Russia', 5, 50, '2023-04-03T00:00:00', '2023-04-09T23:59:59')
        time.sleep(0.1)
        news = get_news('Russia', 15, 50, '2023-04-03T00:00:00', '2023-04-09T23:59:59')
        dt = round((time.time_ns() - t1) / 1000000000, 4)
        print(f'time = {dt}s')
        # time = 4.2-5.9s (for 3 queries * 10 news)
        # time = 4.1-5.8s (for 3 queries * 50 news)
        totalCount = get_json_value(news, ['totalCount'])
        bot.reply_to(message, totalCount)
    except (requests.RequestException, requests.exceptions.JSONDecodeError,
            ValueError) as exception:
        logger.exception(exception)
        # TODO: be more specific?
        bot.reply_to(
            message, 'Some error occurred. You may have entered an invalid data')
