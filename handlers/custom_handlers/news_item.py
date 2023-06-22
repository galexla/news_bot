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
    chat_id, user_id = call.message.chat.id, call.message.from_user.id

    try:
        title, url, _, _ = top_news.get_cached_top_news(news_id)

        bot.send_message(chat_id, f'*{title}*',
                         reply_markup=news_menu.news_item(news_id, url),
                         parse_mode='Markdown')
    except ValueError:
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

    title, url, body, ttl = top_news.get_cached_top_news(news_id)
    if not title or not url:
        logger.error(f'Unable to get summary for news id "{news_id}"')
        bot.send_message(chat_id, '*Unable to get news summary.*',
                         parse_mode='Markdown')
    else:
        summary = cache.get_set(cache.key('article_summary', news_id), ttl,
                                get_summary, body)
        summary = ' '.join(summary)

        text_msg = f'*Summary of article "{title}"*:\n{summary}'
        bot.send_message(chat_id, text_msg, parse_mode='Markdown')
