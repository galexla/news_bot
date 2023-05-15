import datetime
import functools
import json
from typing import Any, Callable

from loguru import logger

from loader import redis_connection

# TODO: remove these comments
# prefixes: summary, summary_input, most_important_news, news_count


def cached(key: str, date_time: str) -> Callable:
    """
    Parametrized decorator for caching function result in Redis

    :param key: cache key
    :type key: str
    :param date_time: date in format %Y-%m-%dT%H:%M:%S
    :type date_time: str
    """
    def decorator(func) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = None
            if redis_connection.exists(key):
                result = get(key)
            else:
                result = func(*args, **kwargs)
                ttl = _get_ttl(date_time)
                set(key, result, ex=ttl)

            logger.debug(f'redis_cache: got {key}: {_get_str_for_log(result)}')

            return result

        return wrapper

    return decorator


def exists(key: str) -> bool:
    """
    Checks if key exists in Redis

    :param key: key
    :type key: str
    :return: True if key exists, False otherwise
    :rtype: bool
    """
    return redis_connection.exists(key)


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


def get_key(*args) -> str:
    """
    Gets Redis key by concatenating key parts with ':' separator

    :param args: key parts
    :type args: Any
    :return: Redis key
    :rtype: str
    """
    return ':'.join(str(arg) for arg in args)


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


def _get_ttl(date_time: str) -> int:
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
