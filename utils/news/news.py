from typing import Tuple

from utils.misc import redis_cache
from utils.news import news_api
from utils.news.important_news import order_news_by_importance
from utils.news.summary_input import get_summary_input

# TODO: add tests
# TODO: add error handling
# TODO: add logging?


def get_news_semimanufactures(search_query: str, date_from: str,
                              date_to: str) -> Tuple[int, str, dict[dict]]:
    """
    Loads news from API and calculates news count, summary input
    and new ordered by importance and caches them to Redis.
    If these entities are already cached loads them from Redis.

    :param search_query: search query
    :type search_query: str
    :param date_from: start date in format %Y-%m-%dT%H:%M:%S
    :type date_from: str
    :param date_to: end date in format %Y-%m-%dT%H:%M:%S
    :type date_to: str
    :return: news count, summary input, news ordered by importance
    :rtype: Tuple[int, str, dict[dict]]
    """
    text_key = 'description'

    news = None
    prefixes = ('news_count', 'summary_input', 'most_important_news')
    if not redis_cache.all_exist(prefixes, search_query, date_from, date_to):
        news = news_api.get_news(search_query, date_from, date_to)

    cached_get_news_count = redis_cache.cached(
        'news_count', search_query, date_from, date_to)(get_news_count)
    news_count = cached_get_news_count(news)

    cached_get_summary_input = redis_cache.cached(
        'summary_input', search_query, date_from, date_to)(get_summary_input)
    summary_input = cached_get_summary_input(news, text_key)

    cached_order_news_by_importance = redis_cache.cached(
        'most_important_news', search_query, date_from, date_to)(order_news_by_importance)
    news_by_importance = cached_order_news_by_importance(news, text_key)

    return news_count, summary_input, news_by_importance


def get_news_count(news: list[dict]) -> int:
    """
    Returns news count.

    :param news: news
    :type news: list[dict]
    :return: news count
    :rtype: int
    """
    return len(news) if news else 0
