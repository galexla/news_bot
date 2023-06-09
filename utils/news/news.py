from typing import Tuple

from utils.misc import redis_cache as cache
from utils.news import news_api
from utils.news.important_news import get_important_news
from utils.news.summary_input import get_summary_input


def get_news_semimanufactures(search_query: str, datetime_from: str,
                              datetime_to: str) -> Tuple[int, str, dict[dict]]:
    """
    Loads news from API and calculates news count, summary input
    and new ordered by importance and caches them to Redis.
    If these entities are already cached loads them from Redis.

    :param search_query: search query
    :type search_query: str
    :param datetime_from: start date in format %Y-%m-%dT%H:%M:%S
    :type datetime_from: str
    :param datetime_to: end date in format %Y-%m-%dT%H:%M:%S
    :type datetime_to: str
    :return: news count, summary input, important news ordered by importance
    :rtype: Tuple[int, str, dict[dict]]
    """
    text_key = 'description'

    news = None
    prefixes = ('news_count', 'summary_input', 'important_news')
    if not cache.all_axists(prefixes, search_query, datetime_from, datetime_to):
        news = news_api.get_news(search_query, datetime_from, datetime_to)

    news_count = cache.get_set(cache.key('news_count',
                               search_query, datetime_from, datetime_to),
                               cache.get_ttl(datetime_to),
                               get_news_count, news)

    summary_input = cache.get_set(cache.key('summary_input',
                                  search_query, datetime_from, datetime_to),
                                  cache.get_ttl(datetime_to),
                                  get_summary_input, news, text_key)

    important_news = cache.get_set(cache.key('important_news',
                                   search_query, datetime_from, datetime_to),
                                   cache.get_ttl(datetime_to),
                                   get_important_news, news, text_key)

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
