import datetime
import json
from typing import Any, Iterable

from loguru import logger

from loader import redis_connection


# prefixes: summary, summary_input, important_news, news_count


def exists(key: str) -> bool:
    """
    Checks if key exists in Redis

    :param key: key
    :type key: str
    :return: True if key exists, False otherwise
    :rtype: bool
    """
    return redis_connection.exists(key)


def all_axists(prefixes: Iterable[str], search_query: str,
               datetime_from: str, datetime_to: str) -> bool:
    return all(exists(key(prefix, search_query, datetime_from, datetime_to))
               for prefix in prefixes)


def key(*key_parts) -> str:
    """
    Creates key by concatenating key parts with ':' separator

    :param key_parts: key parts
    :type key_parts: Any
    :return: Redis key
    :rtype: str
    """
    return ':'.join(str(part) for part in key_parts)


def _get_str_for_log(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return f'count={len(value)}'
    if isinstance(value, str):
        return f'{value[:100]}...'
    return value


def get(key) -> Any:
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


def get_by_params(prefix: str, search_query: str,
                  datetime_from: str, datetime_to: str) -> Any:
    key = key(prefix, search_query, datetime_from, datetime_to)
    return get(key)


def get_set(key: str, ttl: int, func: callable, *args, **kwargs) -> Any:
    """
    Gets func result if cached. Or caclculates and caches it with func and its *args

    :param key: key
    :type key: str
    :param ttl: TTL in seconds
    :type ttl: int
    :param func: function for caclculating results if it is not cached
    :type func: callable
    :param *args: func arguments
    :type *args: Any
    :param *kwargs: func arguments
    :type *kwargs: Any
    :rtype: Any
    :return: result
    """
    result = None
    if redis_connection.exists(key):
        result = get(key)
    else:
        result = func(*args, **kwargs)
        set(key, result, ex=ttl)

    logger.debug(f'redis_cache: got {key}: {_get_str_for_log(result)}')

    return result


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


def get_ttl(date_time: str) -> int:
    """
    Gets TTL in seconds for Redis key

    :param date_time: date of the cached item in format %Y-%m-%dT%H:%M:%S
    :type date_time: str
    :return: TTL
    :rtype: int
    """
    date_time = datetime.datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S')
    timestamp = datetime.datetime.timestamp(date_time)
    now_timestamp = datetime.datetime.utcnow().timestamp()

    if now_timestamp - timestamp >= 3600 * 3:
        return 3600 * 24 * 90
    return 3600 * 3
