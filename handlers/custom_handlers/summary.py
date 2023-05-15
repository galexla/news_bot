import requests
from loguru import logger
from telebot.types import CallbackQuery

from loader import bot
from states.news_state import NewsState
from utils import get_summary
from utils.misc import redis_cache as cache
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
        news_utils.retrieve_user_input(chat_id, user_id)

    try:
        key_summary_input = cache.get_key(
            'summary_input', search_query, datetime_from, datetime_to)
        summary_input = cache.get(key_summary_input)
        if not summary_input:
            raise ValueError('No summary input found.')

        key_summary = cache.get_key(
            'summary', search_query, datetime_from, datetime_to)
        cached_get_summary = cache.cached(
            key_summary, datetime_to)(get_summary)
        summary_text = cached_get_summary(summary_input)

        if summary_text:
            bot.send_message(chat_id, summary_text)
        else:
            bot.send_message(chat_id, 'Unable to get summary.')
    except (requests.RequestException, ValueError,
            requests.exceptions.JSONDecodeError) as exception:
        logger.exception(exception)
        bot.send_message(chat_id, 'Some error occurred.')
