from datetime import date
from typing import Tuple

from utils.misc import redis_cache as cache
from utils.news import news_api
from utils.news.important_news import get_important_news
from utils.news.summary_input import get_summary_input

TEXT_KEY = 'description'
REDIS_PREFIXES = ('news_count', 'summary_input', 'important_news')


def get_news_semimanufactures(search_query: str, date_from: date,
                              date_to: date) -> Tuple[int, str, dict[dict]]:
    """
    Loads news from API and calculates news count, summary input
    and new ordered by importance and caches them to Redis.
    If these entities are already cached loads them from Redis.

    :param search_query: search query
    :type search_query: str
    :param date_from: start date
    :type date_from: date
    :param date_to: end date
    :type date_to: date
    :return: news count, summary input, important news ordered by importance
    :rtype: Tuple[int, str, dict[dict]]
    """
    news = None
    if not cache.all_exist(REDIS_PREFIXES, search_query, date_from, date_to):
        news = news_api.get_news(search_query, date_from, date_to)

    news_count = cache.get_set(
        cache.key_query('news_count', search_query, date_from, date_to),
        cache.calc_ttl(date_to),
        get_news_count, news)

    summary_input = cache.get_set(
        cache.key_query('summary_input', search_query, date_from, date_to),
        cache.calc_ttl(date_to),
        get_summary_input, news, TEXT_KEY)

    important_news = cache.get_set(
        cache.key_query('important_news', search_query, date_from, date_to),
        cache.calc_ttl(date_to),
        get_important_news, news, TEXT_KEY)

    return news_count, summary_input, important_news


def get_news_count(news: list[dict]) -> int:
    """
    Returns news count.

    :param news: news
    :type news: list[dict]
    :return: news count
    :rtype: int
    """
    return len(news) if news else 0
