import datetime
import re
from typing import Tuple

from telebot.types import Message

from loader import bot


def get_search_data(chat_id: int, user_id: int) -> Tuple[str, str, str, str, str]:
    """
    Gets saved news search data

    :param message: incoming message
    :type message: Message
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
        datetime.datetime.fromisoformat(date)
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
        datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False
