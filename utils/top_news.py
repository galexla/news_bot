from datetime import date
from typing import Tuple

from config_data import config
from utils.misc import redis_cache as cache

TEXT_KEYS = (config.NEWS_TITLE, config.NEWS_BODY)


def get_top_news(
    sentences: list[str], important_news: dict[dict], n_max: int = 5
) -> list[dict]:
    """
    Tries to get top 5 news

    :param sentences: sentences
    :type sentences: list[str]
    :param important_news: news: {id: {importance: float, news: dict}, ...}
    :type important_news: dict[dict]
    :param n_max: max number of news to return
    :type n_max: int
    :return: top 5 news
    :rtype: list[dict]
    """
    top_news = []
    i_item = 0
    for news_id in important_news:
        top_news.append(important_news[news_id]['news'])
        i_item += 1
        if i_item >= n_max:
            break

    return top_news[:n_max]


def cache_top_news_items(top_news: list[dict], date_to: date) -> None:
    """
    Caches top news

    :param top_news: top news
    :type top_news: list[dict]
    :param date_to: end date of a news search query to calculate cache ttl
    :type date_to: date
    """
    for news_item in top_news:
        key = cache.key('top_news_item', news_item[config.NEWS_ID])
        if not cache.exists(key):
            cache.set(key, news_item, ex=cache.calc_ttl(date_to))


def get_cached_top_news_item(id: str) -> Tuple[dict | None, int]:
    """
    Returns top news item and ttl

    :param id: news id
    :type id: str
    :return: title and url
    :rtype: Tuple[dict | None, int]
    """
    key = cache.key('top_news_item', id)
    if cache.exists(key):
        news_item = cache.get(key)
        return news_item, cache.get_ttl(key)
    return None, 0
