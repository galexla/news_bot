import requests
from loguru import logger
from telebot.types import CallbackQuery

from loader import bot
from states.news_state import NewsState
from utils import get_summary
from utils.misc import redis_cache
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


    key = redis_cache.get_key('summary_input', search_query,
                              datetime_from, datetime_to)
    summary_input = redis_cache.get(key)
    try:
        summary_text = _get_summary(
            search_query, datetime_from, datetime_to, summary_input)
        if summary_text:
            bot.send_message(chat_id, summary_text)
        else:
            bot.send_message(chat_id, 'No summary found.')
    except (requests.RequestException,
            requests.exceptions.JSONDecodeError) as exception:
        logger.exception(exception)
        bot.send_message(chat_id, 'Some error occurred.')


@redis_cache.cached('summary')
def _get_summary(search_query: str, datetime_from: str, datetime_to: str,
                 summary_input: str) -> str:
    """
    Gets summary from cache or from API

    :param search_query: search query
    :type search_query: str
    :param datetime_from: datetime from
    :type datetime_from: str
    :param datetime_to: datetime to
    :type datetime_to: str
    :param summary_input: summary input
    :type summary_input: str
    :rtype: str
    """
    return get_summary(summary_input)
