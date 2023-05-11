import requests
from loguru import logger
from telebot.types import CallbackQuery

from loader import bot
from states.news_state import NewsState
from utils import get_summary
from utils.news import utils as news_utils


@bot.callback_query_handler(func=lambda call: call.data == 'summary', state=NewsState.got_news)
def bot_summary(call: CallbackQuery):
    """
    Gets summary

    :param call: callback query
    :type call: CallbackQuery
    :rtype: None
    """
    logger.debug('bot_summary() called')

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    search_query, datetime_from, datetime_to, _, _ = \
        news_utils.get_search_data(chat_id, user_id)

    try:
        summary_text = get_summary(search_query, datetime_from, datetime_to)
        if summary_text:
            bot.send_message(chat_id, summary_text)
        else:
            bot.send_message(chat_id, 'No summary found.')
    except requests.RequestException as exception:
        logger.exception(exception)
        bot.send_message(chat_id, 'Some error occurred.')
