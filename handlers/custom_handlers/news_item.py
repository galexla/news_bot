import re

from loguru import logger
from telebot.types import CallbackQuery

from keyboards.reply import news_menu
from loader import bot
from states.news_state import NewsState
from utils.misc import redis_cache as cache
from utils.misc.user_info import retrieve_user_info
from utils.summary import get_summary


@bot.callback_query_handler(func=lambda call: call.data.startswith('news_'), state=NewsState.got_news)
def bot_click_news_item(call: CallbackQuery):
    """
    Handles news item click

    :param call: callback query
    :type call: CallbackQuery
    :rtype: None
    """
    logger.debug('bot_news_item() called')
    chat_id, user_id, search_query, datetime_from, datetime_to = \
        retrieve_user_info(call)

    news_id = re.search(r'^news_(\d+)$', call.data).group(1).strip()

    try:
        important_news = cache.get(cache.key(
            'important_news', search_query, datetime_from, datetime_to))

        news_item = important_news[news_id]['news']
        title = news_item['title']
        url = news_item['url']

        bot.send_message(
            chat_id, title, reply_markup=news_menu.news_item(news_id, url))
    except ValueError as exception:
        logger.error(
            f'Error occurred while fetching news item: {news_id} for user: '
            f'{user_id}, with search parameters: "{search_query}", '
            f'{datetime_from}, {datetime_to}')
        bot.send_message(chat_id, 'Some error occurred.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('summary_'), state=NewsState.got_news)
def bot_news_summary(call: CallbackQuery):
    """
    Gets summary of a news article

    :param call: callback query
    :type call: CallbackQuery
    :rtype: None
    """
    logger.debug('bot_news_summary() called')

    chat_id, _, search_query, datetime_from, datetime_to = \
        retrieve_user_info(call)

    news_id = re.search(r'^summary_(\d+)$', call.data).group(1).strip()

    important_news = cache.get(cache.key(
        'important_news', search_query, datetime_from, datetime_to))

    if not important_news:
        logger.error(f'Unable to get top news for query: "{search_query}", '
                     f'{datetime_from} - {datetime_to}.')
        bot.send_message(chat_id, 'Unable to get news summary.')
        return

    news_item = important_news[news_id]['news']

    summary = cache.get_set(cache.key('article_summary', news_id),
                            cache.get_ttl(datetime_to),
                            get_summary, news_item['body'])
    summary = ' '.join(summary)

    title = news_item['title']
    text_msg = f'Summary of article "{title}": \n{summary}'
    bot.send_message(chat_id, text_msg)
