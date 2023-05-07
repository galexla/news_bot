import json
from typing import Optional

from loader import redis_connection


def cache_summary_input(search_query: str, date_from: str, date_to: str, text: str) -> None:
    """
    Caches text to be summarized to Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date
    :type date_from: str
    :param date_to: end date
    :type date_to: str
    :param text: text
    :type text: str
    :return: None
    """
    prefix = 'summary_input'
    key = f'{prefix}:{search_query}:{date_from}:{date_to}'
    redis_connection.set(key, text)


def cache_most_important_news(search_query: str, date_from: str, date_to: str, news: list[dict]) -> None:
    """
    Caches most important news to Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date
    :type date_from: str
    :param date_to: end date
    :type date_to: str
    :param news: news
    :type news: list[dict]
    :return: None
    """
    prefix = 'most_important_news'
    key = f'{prefix}:{search_query}:{date_from}:{date_to}'
    redis_connection.set(key, json.dumps(news))


def get_most_important_news(search_query: str, date_from: str, date_to: str) -> Optional[list[dict]]:
    """
    Gets most important news from Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date
    :type date_from: str
    :param date_to: end date
    :type date_to: str
    :return: most important news
    :rtype: list[dict]
    """
    prefix = 'most_important_news'
    key = f'{prefix}:{search_query}:{date_from}:{date_to}'
    news = redis_connection.get(key)

    if news is None:
        return None
    return json.loads(news)


def get_summary_input(search_query: str, date_from: str, date_to: str) -> Optional[str]:
    """
    Gets text to be summarized from Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date
    :type date_from: str
    :param date_to: end date
    :type date_to: str
    :return: text to be summarized
    :rtype: str
    """
    prefix = 'summary_input'
    key = f'{prefix}:{search_query}:{date_from}:{date_to}'
    text = redis_connection.get(key)

    return text
