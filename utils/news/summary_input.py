import re
from typing import Iterable

from config_data import config

MAX_NEWS_COUNT = 30
SUMMARY_MAX_INPUT = 30000
UNIQUE_KEY = config.NEWS_BODY


def get_summary_input(news: Iterable[dict], text_key: str) -> str:
    """
    Gets text for summary

    :param news: news
    :type news: Iterable[dict]
    :param text_key: field to get text from
    :type text_key: str
    :return: text for summary
    :rtype: str
    """
    news = _get_unique_news(news)
    average_length = _get_average_length(news, text_key)
    news_count = round(SUMMARY_MAX_INPUT / average_length)
    news_count = min(news_count, len(news), MAX_NEWS_COUNT)
    text_for_summary = _join_news(
        news[:news_count], text_key, 2.5 * average_length
    )

    return text_for_summary


def _get_unique_news(news: Iterable[dict]) -> list[dict]:
    """
    Returns a copy of news where no duplicates of value of key present

    :param news: news
    :type news: list[dict]
    :return: news with no duplicates
    :rtype: list[dict]
    """
    result = []
    added_news = set()
    for item in news:
        text_value = _remove_symbols_numbers(item[UNIQUE_KEY])
        if text_value != '' and text_value not in added_news:
            added_news.add(text_value)
            result.append(item)

    return result


def _remove_symbols_numbers(text: str) -> str:
    """
    Removes symbols and numbers from text

    :param text: text
    :type text: str
    :return: text without symbols and numbers
    :rtype: str
    """
    pattern = r'[\W\d]+'
    empty_str = ''
    text = re.sub(pattern, empty_str, text)

    return text.lower()


def _get_average_length(news: list, key: str) -> int:
    """
    Calculates the average length of a news item

    :param news: list of news
    :type news: list
    :param key: field name to calculate the average length of
    :type key: str
    :raises ValueError: raised if news list is empty
    :raises ValueError: raised if key is empty
    :return: average length of a news item
    :rtype: int
    """
    if len(news) == 0:
        raise ValueError('News list is empty')

    if len(key) == 0:
        raise ValueError('Key is empty')

    total_length = 0

    for news_item in news:
        total_length += len(news_item[key])

    if total_length == 0:
        raise ValueError('Total length is zero')

    average_length = round(total_length / len(news))

    return average_length


def _clean_news_text(text: str) -> str:
    """
    Cleans news text and adds a dot at the end if it's missing

    :param text: text to clean
    :type text: str
    :return: cleaned text
    :rtype: str
    """
    text = text.lstrip(' \n\r\t')
    text = text.rstrip(' \n\r\t:;,-‐‑‒﹣－')
    if not text.endswith(('!', '?', '…', '.')):
        text += '.'
    text = re.sub(r'[\t ]{2,}', ' ', text, flags=re.MULTILINE)

    return text


def _join_news(
    news: list[dict], key: str, max_item_length: int, sep: str = '\n\n'
) -> str:
    """
    Joins news text

    :param news: news
    :type news: list[dict]
    :param key: field to get text from
    :type key: str
    :param max_item_length: longer cleaned news texts are skipped
    :type max_item_length: int
    :param sep: a separator to join news
    :type sep: str
    :return: joined news
    :rtype: str
    """
    result = ''
    total_length = 0
    for item in news:
        item_text = _clean_news_text(item[key]) + sep
        if len(item_text) > max_item_length:
            continue
        total_length += len(item_text)
        if total_length > SUMMARY_MAX_INPUT:
            continue
        result += item_text

    return result
