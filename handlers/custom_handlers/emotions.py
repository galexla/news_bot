import re

import requests
from loguru import logger
from telebot.types import CallbackQuery

from loader import bot
from states.news_state import NewsState
from utils.emotions import get_emotions
from utils.misc import get_text_excerpts, redis_cache
from utils.news import utils as news_utils


@bot.callback_query_handler(func=lambda call: call.data.startswith('emotions_'), state=NewsState.got_news)
def bot_emotions(call: CallbackQuery):
    """
    Gets emotions from a news article using GPT-3 chatbot

    :param call: callback query
    :type call: CallbackQuery
    :rtype: None
    """
    logger.debug('bot_emotions() called')

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    news_id = re.search(r'^emotions_(\d+)$', call.data).group(1).strip()

    search_query, datetime_from, datetime_to, _, _ = \
        news_utils.retrieve_user_input(chat_id, user_id)

    try:
        key = redis_cache.get_key('most_important_news', search_query,
                                  datetime_from, datetime_to)
        most_important_news = redis_cache.get(key)
        if not most_important_news:
            raise ValueError('Most important news not found.')

        news_item = most_important_news[news_id]['news']
        text = news_item['body']
        text = get_text_excerpts(text, 2000)

        key_emotions = redis_cache.get_key('emotions', news_id)
        cached_get_emotions = redis_cache.cached(
            key_emotions, datetime_to)(get_emotions)
        emotions = cached_get_emotions(text)

        if emotions:
            title = news_item['title']
            message_text = f'Emotions in the news article "{title}":\n{emotions}'
            bot.send_message(chat_id, message_text)
        else:
            bot.send_message(chat_id, 'Unable to get emotions.')
    except (requests.RequestException, ValueError,
            requests.exceptions.JSONDecodeError) as exception:
        logger.exception(exception)
        bot.send_message(chat_id, 'Some error occurred.')
