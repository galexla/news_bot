import re

from loguru import logger
from telebot.types import CallbackQuery

from keyboards.reply import news_menu
from loader import bot
from utils import top_news
from utils.misc import redis_cache as cache
from utils.summary import get_summary


@bot.callback_query_handler(func=lambda call: call.data.startswith('news_'), state=None)
def bot_click_news_item(call: CallbackQuery):
    """
    Handles news item click

    :param call: callback query
    :type call: CallbackQuery
    :rtype: None
    """
    logger.debug('bot_click_news_item()')

    news_id = re.search(r'^news_(\d+)$', call.data).group(1).strip()
    chat_id, user_id = call.message.chat.id, call.from_user.id

    news_item, _ = top_news.get_cached_top_news(news_id)
    if news_item:
        title, url = news_item['title'], news_item['url']
        bot.send_message(chat_id, f'*{title}*',
                         reply_markup=news_menu.news_item(news_id, url),
                         parse_mode='Markdown')
    else:
        logger.error(
            f'Error occurred while fetching news item: {news_id} for user: '
            f'{user_id} in chat: {chat_id}.')
        bot.send_message(chat_id, '*Some error occurred.*',
                         parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith('summary_'), state=None)
def bot_news_summary(call: CallbackQuery):
    """
    Gets summary of a news article

    :param call: callback query
    :type call: CallbackQuery
    :rtype: None
    """
    logger.debug('bot_news_summary()')

    news_id = re.search(r'^summary_(\d+)$', call.data).group(1).strip()
    chat_id = call.message.chat.id

    news_item, ttl = top_news.get_cached_top_news(news_id)
    if news_item:
        summary = cache.get_set(cache.key('article_summary', news_id), ttl,
                                get_summary, news_item['body'])
        summary = ' '.join(summary)

        title = news_item['title']
        text_msg = f'*Summary of article "{title}"*:\n{summary}'
        bot.send_message(chat_id, text_msg, parse_mode='Markdown')
    else:
        logger.error(f'Unable to get summary for news id "{news_id}"')
        bot.send_message(chat_id, '*Unable to get news summary.*',
                         parse_mode='Markdown')
