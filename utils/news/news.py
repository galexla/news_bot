from datetime import date
from typing import Iterable, Tuple

from config_data import config
from utils.misc import redis_cache as cache
from utils.news import news_api
from utils.news.important_news import get_important_news
from utils.news.summary_input import get_summary_input

IMPORTANT_NEWS_KEYS = (
    config.NEWS_TITLE, config.NEWS_DESCRIPTION, config.NEWS_BODY)


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
    KEY_PREFIXES = ('news_count', 'important_news')

    news = None
    if not cache.all_exist(KEY_PREFIXES, search_query, date_from, date_to):
        news, n_news_total = news_api.get_news(
            search_query, date_from, date_to)

        cache.set(
            cache.key_query('news_count', search_query, date_from, date_to),
            n_news_total,
            cache.calc_ttl(date_to))

        important_news = get_important_news(search_query, news, IMPORTANT_NEWS_KEYS)
        cache.set(
            cache.key_query('important_news', search_query, date_from, date_to),
            important_news,
            cache.calc_ttl(date_to))
    else:
        n_news_total = cache.get(
            cache.key_query('news_count', search_query, date_from, date_to))

        important_news = cache.get(
            cache.key_query('important_news', search_query, date_from, date_to))

    if n_news_total == 0:
        return 0, '', {}

    key = cache.key_query('summary_input', search_query, date_from, date_to)
    if cache.exists(key):
        summary_input = cache.get(key)
    else:
        news_for_summary = important_news_to_iterator(important_news)
        summary_input = get_summary_input(
            news_for_summary, config.NEWS_DESCRIPTION)
        cache.set(key, summary_input, cache.calc_ttl(date_to))

    return n_news_total, summary_input, important_news


def important_news_to_iterator(important_news: dict[dict]) -> Iterable[dict]:
    """
    Converts important news to iterator.

    :param important_news: important news
    :type important_news: dict[dict]
    :return: important news iterator
    :rtype: Iterable[dict]
    """
    return (item[1]['news'] for item in important_news.items())
