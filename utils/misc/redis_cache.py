import json
from datetime import date, datetime
from typing import Any, Iterable

from loguru import logger

from loader import redis_connection
from utils.news.utils import date_from_to_str, date_to_to_str

FRESH_RECORD_TTL = 3600 * 3
OLD_RECORD_TTL = 3600 * 24 * 7
FRESH_OLD_THRESHOLD = 3600 * 24 * 2

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


def all_exist(prefixes: Iterable[str], search_query: str,
              date_from: date, date_to: date) -> bool:
    """
    Checks if all keys with specified prefixes exist in Redis

    :param prefixes: prefixes
    :type prefixes: Iterable[str]
    :param search_query: search query
    :type search_query: str
    :param date_from: date from
    :type date_from: date
    :param date_to: date to
    :type date_to: date
    :return: True if all keys exist, False otherwise
    :rtype: bool
    """
    return all(exists(key_query(prefix, search_query, date_from, date_to))
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


def key_query(prefix: str, search_query: str, date_from: date,
              date_to: date) -> str:
    """
    Creates key for query

    :param prefix: prefix
    :type prefix: str
    :param search_query: search query
    :type search_query: str
    :param date_from: date from
    :type date_from: date
    :param date_to: date to
    :type date_to: date
    :return: Redis key
    :rtype: str
    """
    date_from = date_from_to_str(date_from)
    date_to = date_to_to_str(date_to)
    return key(prefix, search_query, date_from, date_to)


def get(key) -> Any:
    """
    Gets value from Redis

    :param key: key
    :type key: str
    :return: value
    :rtype: Any
    """
    value = redis_connection.get(key)
    if value is None:
        logger.info(f'Key {key} not found in Redis')
    return _cast_type(value)


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


def get_ttl(key: str) -> int:
    """
    Gets TTL of key

    :param key: key
    :type key: str
    :return: TTL
    :rtype: int
    """
    return redis_connection.ttl(key)


def set(key: str, value: Any, ex: int = None) -> None:
    """
    Sets value to Redis

    :param key: key
    :type key: str
    :param value: value
    :type value: Any
    :param ex: TTL in seconds
    :type ex: int
    :rtype: None
    """
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    redis_connection.set(key, value, ex=ex)


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


def _get_str_for_log(value: Any) -> str:
    """
    Gets string for logging

    :param value: value
    :type value: Any
    :return: string for logging
    :rtype: str
    """
    if isinstance(value, (dict, list)):
        return f'count={len(value)}'
    if isinstance(value, str):
        if len(value) > 100:
            return f'{value[:100]}...'
        return value
    return value


def calc_ttl(date_to: date) -> int:
    """
    Calculates TTL in seconds for give date_to of a search query

    :param date_to: date to
    :type date_to: date
    :return: TTL
    :rtype: int
    """
    date_to = datetime.combine(date_to, datetime.max.time())
    now = datetime.utcnow().timestamp()

    if now - date_to.timestamp() >= FRESH_OLD_THRESHOLD:
        return OLD_RECORD_TTL
    return FRESH_RECORD_TTL
