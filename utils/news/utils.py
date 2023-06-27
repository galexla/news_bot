import functools
from datetime import date, timedelta
from typing import Iterable, Iterator


def get_first_day_of_week(date: date) -> date:
    """
    Gets first day of week (Monday) for date

    :param date: date
    :type date: date
    :return: first day of week
    :rtype: date
    """
    return date - timedelta(days=date.weekday())


def get_last_day_of_week(date: date) -> date:
    """
    Gets last day of week (Sunday) for date

    :param date: date
    :type date: date
    :return: last day of week
    :rtype: date
    """
    return date + timedelta(days=6 - date.weekday())


def news_to_texts(news: list[dict], text_keys: Iterable[str],
                  separator: str = '\n\n') -> Iterator[str]:
    """
    Converts news to iterator of texts

    :param news: news
    :type news: list[dict]
    :param text_keys: keys to get text from
    :type text_keys: Iterable[str]
    :param separator: text separator
    :type separator: str
    :yield: text
    :ytype: str
    """
    for news_item in news:
        text = to_text(news_item, text_keys, separator)
        yield text


def to_text(news_item: dict, text_keys: Iterable[str],
            separator: str = '\n\n') -> str:
    """
    Joins all text_keys contents to text

    :param news_item: news item
    :type news_item: dict
    :param text_keys: keys to get text from
    :type text_keys: Iterable[str]
    :param separator: text separator
    :type separator: str
    :return: text
    :rtype: str
    """
    return separator.join(news_item.get(key, '') for key in text_keys)


def important_news_to_texts(news: dict[dict], text_keys: Iterable[str],
                            separator: str = '\n\n') -> dict[str, str]:
    """
    Converts important news to iterator of texts

    :param news: news in format {news_id: {'importance': bool, 'news': dict}, ...}
    :type news: dict[dict]
    :param text_keys: keys to get text from
    :type text_keys: Iterable[str]
    :param separator: text separator
    :type separator: str
    :return: result in format {news_id: text, ...}
    :rtype: dict[str, str]
    """
    result = {}
    for news_id, item in news.items():
        news_item = item['news']
        text = to_text(news_item, text_keys, separator)
        result[news_id] = text

    return result


@functools.lru_cache(maxsize=128)
def date_from_to_str(date_from: date) -> str:
    """
    Converts date to string in format %Y-%m-%dT00:00:00

    :param date_from: date
    :type date_from: date
    :return: date in format %Y-%m-%dT00:00:00
    :rtype: str
    """
    return date_from.strftime('%Y-%m-%dT00:00:00')


@functools.lru_cache(maxsize=128)
def date_to_to_str(date_to: date) -> str:
    """
    Converts date to string in format %Y-%m-%dT23:59:59

    :param date_to: date
    :type date_to: date
    :return: date in format %Y-%m-%dT23:59:59
    :rtype: str
    """
    return date_to.strftime('%Y-%m-%dT23:59:59')
