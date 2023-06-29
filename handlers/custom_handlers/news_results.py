from datetime import date

import requests
from loguru import logger

from keyboards.reply import news_menu
from loader import bot
from states.news_state import NewsState
from utils.misc import redis_cache as cache
from utils.news.news import get_news_semimanufactures
from utils.summary import get_summary
from utils.top_news import cache_top_news, get_top_news


def get_results(chat_id: int, user_id: int, search_query: str,
                date_from: date, date_to: date) -> None:
    """
    Gets and displays news count, summary and top news

    :param chat_id: chat id
    :type chat_id: int
    :param user_id: user id
    :type user_id: int
    :param search_query: search query
    :type search_query: str
    :param date_from: date from
    :type date_from: date
    :param date_to: date to
    :type date_to: date
    :rtype: None
    """
    date_from_str = date_from.strftime('%d.%m.%Y')
    date_to_str = date_to.strftime('%d.%m.%Y')

    text_msg = f'*Getting news from {date_from_str} to {date_to_str} for ' \
        f'search query "{search_query}". It can take up to 6 seconds.*'
    bot.send_message(chat_id, text_msg, parse_mode='Markdown')

    try:
        news_count, summary_input, important_news = get_news_semimanufactures(
            search_query, date_from, date_to)

        text_msg = f'*Got {news_count} news. ' \
            f'Generating summary and top news...*'
        bot.send_message(chat_id, text_msg, parse_mode='Markdown')

        summary, top_news = _get_summary_and_top_news(
            search_query, date_from, date_to,
            summary_input, important_news)

        if summary and top_news:
            bot.set_state(user_id, NewsState.got_news, chat_id)
            _display_summary_and_top_news(chat_id, summary, top_news)
            bot.delete_state(user_id, chat_id)
        else:
            bot.delete_state(user_id, chat_id)
            logger.error(
                f'Unable to get summary & top news for query: '
                f'"{search_query}", period: {date_from} - {date_to}.')
            bot.send_message(chat_id, '*Unable to get top news.*',
                             parse_mode='Markdown')
    except (requests.RequestException, requests.exceptions.JSONDecodeError,
            ValueError) as exception:
        bot.delete_state(user_id, chat_id)
        logger.exception(exception)
        if isinstance(exception, ValueError):
            bot.send_message(chat_id, '*Error. Invalid data.*',
                             parse_mode='Markdown')
        else:
            bot.send_message(chat_id, '*Some error occurred.*',
                             parse_mode='Markdown')


def _get_summary_and_top_news(search_query: str, date_from: date, date_to: date,
                              summary_input: str, important_news: dict) -> tuple[list, list]:
    """
    Gets summary and top news and saves in cache if needed
    
    :param search_query: search query
    :type search_query: str
    :param date_from: date from
    :type date_from: date
    :param date_to: date to
    :type date_to: date
    :param summary_input: summary input
    :type summary_input: str
    :param important_news: important news
    :type important_news: dict
    :return: summary and top news
    :rtype: tuple[list, list]
    """
    summary = cache.get_set(
        cache.key_query('summary', search_query, date_from, date_to),
        cache.calc_ttl(date_to),
        get_summary, summary_input)

    top_news = cache.get_set(
        cache.key_query('top_news', search_query, date_from, date_to),
        cache.calc_ttl(date_to),
        get_top_news, summary, important_news)

    cache_top_news(top_news, date_to)

    return summary, top_news


def _display_summary_and_top_news(chat_id: str, summary: list[str],
                                  top_news: list[dict]) -> None:
    """
    Displays summary and top news
    
    :param chat_id: chat id
    :type chat_id: str
    :param summary: summary
    :type summary: list[str]
    :param top_news: top news
    :type top_news: list[dict]
    :rtype: None
    """
    text_msg = '*Here is summary of news for the chosen period:*\n'
    text_msg = text_msg + ' '.join(summary)
    bot.send_message(chat_id, text_msg, parse_mode='Markdown')

    text_msg = '*Here are top news. You can choose one to get ' \
        'its summary or read the full article.*'
    bot.send_message(chat_id, text_msg, reply_markup=news_menu.main(top_news),
                     parse_mode='Markdown')
