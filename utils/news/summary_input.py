import re
from random import randint
from typing import Callable, Iterator


def get_summary_input(news: list[dict], key: str) -> str:
    """
    Gets text for summary

    :param news: news
    :type news: list[dict]
    :param key: field to get text from
    :type key: str
    :return: text for summary
    :rtype: str
    """
    news = _get_unique_news(news)
    average_length = _get_average_length(news, key)
    news_count = _get_news_count_for_summary(news, average_length)
    news_for_summary = _get_news_for_summary(news, news_count)
    text_for_summary = _join_news(news_for_summary, key)

    return text_for_summary


def _get_unique_news(news: list[dict]) -> list[dict]:
    """
    Returns a copy of news where no duplicates of value of key present

    :param news: news
    :type news: list[dict]
    :return: news with no duplicates
    :rtype: list[dict]
    """
    result = []
    added_news = set()
    pattern, empty_str = r'[\W\d]+', ''
    for item in news:
        body = re.sub(pattern, empty_str, item['body']).lower()
        description = re.sub(pattern, empty_str, item['description']).lower()
        if body not in added_news and description not in added_news:
            added_news.add(body)
            added_news.add(description)
            result.append(item)

    return result


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


def _get_news_count_for_summary(news: list[dict], average_length: int) -> int:
    """
    Calculates the number of news to be used for summary generation

    :news: list of news
    :type news: list[dict]
    :param average_length: average length of a news item
    :type average_length: int
    :raises ValueError: raised if news list is empty
    :raises ValueError: raised if average length is less or equal to zero
    :return: number of news to be used for summary generation
    :rtype: int
    """
    if len(news) == 0:
        raise ValueError('News list is empty')

    if average_length <= 0:
        raise ValueError('Average length must be greater than zero')

    max_summary_input = 50000
    min_news_count = 50

    if len(news) < min_news_count:
        return len(news)

    news_count = round(max_summary_input / average_length)
    news_count = max(min_news_count, news_count)
    news_count = min(len(news), news_count)

    return news_count


def _get_news_for_summary(news: list[dict], n_chunks: int) -> list[dict]:
    """
    Splits a list of news into chunks and returns a random news item from each chunk

    :param news: list of news
    :type news: list[dict]
    :param n_chunks: number of chunks
    :type n_chunks: int
    :raises ValueError: raised if news list is empty
    :raises ValueError: raised if number of chunks is less or equal to zero
    :return: list of random news items
    :rtype: list[dict]
    """
    if len(news) == 0:
        raise ValueError('News list is empty')

    if n_chunks <= 0:
        raise ValueError('Number of chunks must be greater than zero')

    result = []
    chunk_size = len(news) / n_chunks
    for i in range(n_chunks):
        start = round(i * chunk_size)
        end = round((i + 1) * chunk_size) - 1
        result.append(news[randint(start, end)])
    return result


def _clean_news_text(text: str) -> str:
    """
    Cleans news text and adds a dot at the end if it's missing

    :param text: text to clean
    :type text: str
    :return: cleaned text
    :rtype: str
    """
    text = text.strip(' \n\r\t[]():;,{}|')
    text = re.sub(r'([^\.\?\!])$', r'\1.', text, flags=re.MULTILINE)
    text = re.sub(r'([\t ]+)', ' ', text, flags=re.MULTILINE)

    return text


def _iterate_news_key(news: list[dict], key: str,
                      callback: Callable[[str], str]) -> Iterator[str]:
    """
    Iterates over news and applies callback to each item

    :param news: news
    :type news: list[dict]
    :param key: field to get text from
    :type key: str
    :param callback: callback to apply to each item
    :type callback: Callable[[str], str]
    :yield: text
    :ytype: str
    """
    for item in news:
        if key not in item:
            continue
        text = callback(item[key])
        if text != '':
            yield text


def _join_news(news: list[dict], key: str) -> str:
    """
    Joins news text

    :param news: news
    :type news: list[dict]
    :param key: field to get text from
    :type key: str
    :return: joined news
    :rtype: str
    """
    news_iter = _iterate_news_key(news, key, _clean_news_text)
    return '\n'.join(news_iter)
