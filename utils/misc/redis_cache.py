import datetime
import functools
import json
from typing import Any, Callable, Iterable

from loguru import logger

from loader import redis_connection

# TODO: remove these comments
# prefixes: summary, summary_input, most_important_news, news_count


def all_exist(prefixes: Iterable[str], search_query: str, date_from: str,
              date_to: str) -> bool:
    """
    Checks if all of keys exist in Redis

    :param keys: keys
    :type keys: Iterable[str]
    :return: True if all of keys exist in Redis, False otherwise
    :rtype: bool
    """
    return all(
        redis_connection.exists(
            get_key(prefix, search_query, date_from, date_to))
        for prefix in prefixes)


def cached(prefix: str, search_query: str, date_from: str, date_to: str) -> Callable:
    def decorator(func) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = get_key(prefix, search_query, date_from, date_to)
            result = None
            if redis_connection.exists(key):
                result = get(key)
            else:
                result = func(*args, **kwargs)
                ttl = _get_ttl(date_to)
                set(key, result, ex=ttl)

            logger.debug(f'Got {prefix}: {_get_str_for_log(result)}')

            return result

        return wrapper

    return decorator


def _get_str_for_log(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return f'count={len(value)}'
    if isinstance(value, str):
        return f'{value[:100]}...'
    return value


def get(key: str) -> Any:
    """
    Gets value from Redis

    :param key: key
    :type key: str
    :return: value
    :rtype: Any
    """
    value = redis_connection.get(key)
    return _cast_type(value)


def set(key: str, value: Any, ex: int = None) -> None:
    """
    Sets value to Redis

    :param key: key
    :type key: str
    :param value: value
    :type value: Any
    :param ex: TTL in seconds
    :type ex: int
    :return: None
    :rtype: None
    """
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    redis_connection.set(key, value, ex=ex)


def get_key(prefix: str, search_query: str, date_from: str,
            date_to: str) -> str:
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


def _cast_type(value: Any) -> Any:
    """
    Tries to cast value to int, float or json

    :param value: value
    :type value: Any
    :return: simple value
    :rtype: Any
    """
    if value is None:
        return value

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        pass

    return value


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
