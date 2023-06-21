import re
from datetime import date, datetime, timedelta
from typing import Iterable, Iterator, Tuple

from loader import bot


def retrieve_query_info(user_id: int, chat_id: int) -> Tuple[str, str, str, str, str]:
    """
    Gets news search data previously input by user

    :param user_id: user id
    :type user_id: int
    :param chat_id: chat id
    :type chat_id: int
    :return: search query, start datetime, end datetime, start date, end date
    :rtype: Tuple[str, str, str, str, str]
    """
    with bot.retrieve_data(user_id, chat_id) as data:
        search_query = data.get('search_query')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        datetime_from = date_from + 'T00:00:00' if date_from else None
        datetime_to = date_to + 'T23:59:59' if date_to else None

    return search_query, datetime_from, datetime_to, date_from, date_to


def is_datetime_valid(date: str) -> bool:
    """
    Validates a date. Correct format is %Y-%m-%dT%H:%M:%S

    :date: The date
    :type date: str
    :return: validation result
    :rtype: bool
    """
    try:
        datetime.fromisoformat(date)
    except:
        return False

    return re.match(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$', date)


def is_date_valid(date: str) -> bool:
    """
    Checks if date is of format YYYY-MM-DD

    :param date: date to check
    :type date: str
    :rtype: bool
    """
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def get_first_day_of_week(date: date) -> date:
    """
    Gets first day of week

    :param date: date
    :type date: date
    :rtype: date
    """
    return date - timedelta(days=date.weekday())


def get_last_day_of_week(date: date) -> date:
    """
    Gets last day of week

    :param date: date
    :type date: date
    :rtype: date
    """
    return date + timedelta(days=6 - date.weekday())


def news_to_texts(news: list[dict], text_keys: Iterable[str],
                  separator: str = '\n\n') -> Iterator[str]:
    """
    Converts news to iterator of texts

    :param news: news
    :type news: list[dict]
    :param text_keys: text keys
    :type text_keys: Iterable[str]
    :rtype: Iterable[str]
    """
    for news_item in news:
        text = to_text(news_item, text_keys, separator)
        yield text


def to_text(news_item: dict, text_keys: Iterable[str],
            separator: str = '\n\n') -> str:
    return separator.join(news_item.get(key, '') for key in text_keys)


def important_news_to_texts(news: dict[dict], text_keys: Iterable[str],
                            separator: str = '\n\n') -> dict[str, str]:
    """
    Converts important news to iterator of texts

    :param news: news
    :type news: dict[dict]
    :param text_keys: text keys
    :type text_keys: Iterable[str]
    :rtype: dict[str, str]
    :return: result in format {news_id: text, ...}
    """
    result = {}
    for news_id, item in news.items():
        news_item = item['news']
        text = to_text(news_item, text_keys, separator)
        result[news_id] = text

    return result


def date_from_to_str(date_from: date) -> str:
    return date_from.strftime('%Y-%m-%dT00:00:00')


def date_to_to_str(date_to: date) -> str:
    return date_to.strftime('%Y-%m-%dT23:59:59')
