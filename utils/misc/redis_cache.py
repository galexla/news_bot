import datetime
import json
from typing import Optional

from loader import redis_connection


def get_summary(search_query: str, date_from: str, date_to: str) -> Optional[str]:
    """
    Gets text summary from Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date
    :type date_from: str
    :param date_to: end date
    :type date_to: str
    :return: text summary
    :rtype: Optional[str]
    """
    key = _get_key('summary', search_query, date_from, date_to)
    summary = redis_connection.get(key)

    return summary


def set_summary(search_query: str, date_from: str, date_to: str, text: str) -> None:
    """
    Caches summary text to Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date
    :type date_from: str
    :param date_to: end date
    :type date_to: str
    :param text: summary text
    :type text: str
    :return: None
    """
    key = _get_key('summary', search_query, date_from, date_to)
    ttl = _get_ttl(date_to)
    redis_connection.set(key, text, ex=ttl)


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
    key = _get_key('summary_input', search_query, date_from, date_to)
    text = redis_connection.get(key)

    return text


def set_summary_input(search_query: str, date_from: str, date_to: str, text: str) -> None:
    """
    Caches text to be summarized to Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date in format 2000-01-01T00:00:00
    :type date_from: str
    :param date_to: end date in format 2000-01-01T00:00:00
    :type date_to: str
    :param text: text
    :type text: str
    :return: None
    """
    key = _get_key('summary_input', search_query, date_from, date_to)
    ttl = _get_ttl(date_to)
    redis_connection.set(key, text, ex=ttl)


def get_most_important_news(search_query: str, date_from: str, date_to: str) -> Optional[dict[dict]]:
    """
    Gets most important news from Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date
    :type date_from: str
    :param date_to: end date
    :type date_to: str
    :return: most important news
    :rtype: Optional[dict[dict]]
    """
    key = _get_key('most_important_news', search_query, date_from, date_to)
    news = redis_connection.get(key)

    if news is None:
        return None
    return json.loads(news)


def set_most_important_news(search_query: str, date_from: str, date_to: str, news: dict[dict]) -> None:
    """
    Caches most important news to Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date in format %Y-%m-%dT%H:%M:%S
    :type date_from: str
    :param date_to: end date in format %Y-%m-%dT%H:%M:%S
    :type date_to: str
    :param news: news
    :type news: list[dict]
    :return: None
    """
    key = _get_key('most_important_news', search_query, date_from, date_to)
    ttl = _get_ttl(date_to)
    redis_connection.set(key, json.dumps(news), ex=ttl)


def get_news_count(search_query: str, date_from: str, date_to: str) -> Optional[int]:
    """
    Gets news count from Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date
    :type date_from: str
    :param date_to: end date
    :type date_to: str
    :return: news count
    :rtype: int
    """
    key = _get_key('news_count', search_query, date_from, date_to)
    count = redis_connection.get(key)

    if count is None:
        return None
    return int(count)


def set_news_count(search_query: str, date_from: str, date_to: str, news: list[dict]) -> None:
    """
    Caches news count to Redis

    :param search_query: search query
    :type search_query: str
    :param date_from: start date in format %Y-%m-%dT%H:%M:%S
    :type date_from: str
    :param date_to: end date in format %Y-%m-%dT%H:%M:%S
    :type date_to: str
    :param news: news
    :type news: list[dict]
    :return: None
    """
    key = _get_key('news_count', search_query, date_from, date_to)
    ttl = _get_ttl(date_to)
    redis_connection.set(key, len(news), ex=ttl)


def _get_key(prefix: str, search_query: str, date_from: str, date_to: str) -> str:
    """
    Gets Redis key

    :param prefix: prefix
    :type prefix: str
    :param search_query: search query
    :type search_query: str
    :param date_from: start date in format %Y-%m-%dT%H:%M:%S
    :type date_from: str
    :param date_to: end date in format %Y-%m-%dT%H:%M:%S
    :type date_to: str
    :return: Redis key
    :rtype: str
    """
    return f'{prefix}:{search_query}:{date_from}:{date_to}'


def _get_ttl(date_to: str) -> int:
    """
    Gets TTL in seconds for Redis key

    :param date_to: end date in news search query in format %Y-%m-%dT%H:%M:%S
    :type date_to: str
    :return: TTL
    :rtype: int
    """
    date_to_datetime = datetime.datetime.strptime(date_to, '%Y-%m-%dT%H:%M:%S')
    date_to_timestamp = datetime.datetime.timestamp(date_to_datetime)
    now_timestamp = datetime.datetime.utcnow().timestamp()

    if now_timestamp - date_to_timestamp >= 3600 * 3:
        return 3600 * 24 * 90
    return 3600 * 3
