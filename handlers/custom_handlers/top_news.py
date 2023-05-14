import requests
from loguru import logger
from telebot.types import CallbackQuery

from loader import bot
from states.news_state import NewsState
from utils.misc import redis_cache
from utils.news import utils as news_utils
from utils.top_news import get_top_news


@bot.callback_query_handler(func=lambda call: call.data == 'top_news', state=NewsState.got_news)
def bot_top_news(call: CallbackQuery):
    """
    Gets top news

    :param call: callback query
    :type call: CallbackQuery
    :rtype: None
    """
    logger.debug('bot_top_news() called')

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    search_query, datetime_from, datetime_to, _, _ = \
        news_utils.retrieve_user_input(chat_id, user_id)

    try:
        key = redis_cache.get_key('most_important_news', search_query,
                                  datetime_from, datetime_to)
        most_important_news = redis_cache.get(key)
        if not most_important_news:
            raise ValueError('Most important news not found.')

        cached_get_top_news = redis_cache.cached(
            'top_news', search_query, datetime_from, datetime_to)(get_top_news)
        top_news = cached_get_top_news(most_important_news)

        if top_news:
            text = top_news_to_str(top_news, most_important_news)
            bot.send_message(chat_id, text)
        else:
            bot.send_message(chat_id, 'Unable to get top news.')
    except (requests.RequestException, ValueError,
            requests.exceptions.JSONDecodeError) as exception:
        logger.exception(exception)
        bot.send_message(chat_id, 'Some error occurred.')


def top_news_to_str(top_news: list[dict], most_important_news: dict[dict]) -> str:
    """
    Converts top news to string

    :param top_news: top news
    :type top_news: list[dict]
    :return: top news in string format
    :rtype: str
    """
    top_news_str = ''
    for i_item, item in enumerate(top_news, 1):
        news = most_important_news[item['id']]['news']
        top_news_str += \
            f'{i_item}. {news["title"]}\n  {news["description"]}\n{news["url"]}\n\n'

    return top_news_str
