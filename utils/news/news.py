from typing import Tuple

from loguru import logger

from utils.misc import redis_cache
from utils.news import news_api
from utils.news.important_news import order_news_by_importance
from utils.news.summary_input import get_summary_input

# TODO: add tests
# TODO: add error handling
# TODO: add logging?


def get_news(search_query: str, date_from: str,
             date_to: str) -> Tuple[int, str, list[dict]]:
    """
    Loads news from API or Redis and caches them to Redis if needed

    :param search_query: search query
    :type search_query: str
    :param date_from: start date in format %Y-%m-%dT%H:%M:%S
    :type date_from: str
    :param date_to: end date in format %Y-%m-%dT%H:%M:%S
    :type date_to: str
    :return: news count, summary input, most important news
    :rtype: Tuple[int, str, list[dict]]
    """
    text_key = 'description'

    news = None
    prefixes = ('news_count', 'summary_input', 'most_important_news')
    if not redis_cache.all_exist(prefixes, search_query, date_from, date_to):
        news = news_api.get_news(search_query, date_from, date_to)

    news_count = _get_news_count(search_query, date_from, date_to, news)
    summary_input = _get_summary_input(
        search_query, date_from, date_to, news, text_key)
    most_important_news = _get_most_important_news(
        search_query, date_from, date_to, news, text_key)

    return news_count, summary_input, most_important_news


@redis_cache.cached('news_count')
def _get_news_count(search_query: str, date_from: str, date_to: str,
                    news: list[dict]) -> int:
    """
    Gets news count

    :param news: news
    :type news: list[dict]
    :return: news count
    :rtype: int
    """
    return len(news) if news is not None else 0


@redis_cache.cached('summary_input')
def _get_summary_input(search_query: str, date_from: str, date_to: str,
                       news: list[dict], text_key: str) -> str:
    """
    Gets summary input
    """
    result = get_summary_input(news, text_key)
    logger.debug(f'Got summary input: {result[:100]}...')

    return result


@redis_cache.cached('most_important_news')
def _get_most_important_news(search_query: str, date_from: str, date_to: str,
                             news: list[dict], text_key: str) -> list[dict]:
    """
    Gets most important news

    :param news: news
    :type news: list[dict]
    :return: most important news
    :rtype: list[dict]
    """
    result = order_news_by_importance(news, text_key)
    logger.debug(f'Got {len(result)} most important news')

    return result
