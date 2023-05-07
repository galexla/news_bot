import math
import re
from datetime import datetime
from random import randint
from typing import Iterable
from loguru import logger

from config_data import config
from utils.misc import (api_request, get_json_value, get_summary_input,
                        order_news_by_importance, redis_cache)

# TODO: add tests
# TODO: add error handling
# TODO: add logging?


def get_news(search_query: str, date_from: str, date_to: str) -> None:
    text_key = 'description'

    summary_input = redis_cache.get_summary_input(
        search_query, date_from, date_to)
    most_important_news = redis_cache.get_most_important_news(
        search_query, date_from, date_to)

    if summary_input:
        logger.debug(
            f'Summary input was found in Redis, len={len(summary_input)}')

    if most_important_news:
        logger.debug(
            f'Most important news was found in Redis, count={len(most_important_news)}')

    if not summary_input or not most_important_news:
        news = _get_news(search_query, date_from, date_to)
        if not summary_input:
            summary_input = get_summary_input(news, text_key)
            logger.debug(f'Got summary input, len={len(summary_input)}')
            redis_cache.cache_summary_input(
                search_query, date_from, date_to, summary_input)

        if not most_important_news:
            most_important_news = order_news_by_importance(news, text_key)
            logger.debug(
                f'Got most important news input, count={len(most_important_news)}')
            redis_cache.cache_most_important_news(
                search_query, date_from, date_to, most_important_news)


def _get_news(search_query: str, date_from: str, date_to: str) -> list[dict]:
    """
    Gets news using WebSearch API

    :param text: query to search
    :type text: str
    :param date_from: start date in format 2000-01-01T00:00:00
    :type date_from: str
    :param date_to: end date in format 2000-01-01T00:00:00
    :type date_to: str
    :raise ValueError: raised when search query is empty
    :raise ValueError: raised when date is invalid
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: news
    :rtype: list[dict]
    """
    news_per_page = 50

    news = []

    start_time = datetime.now()
    n_news_total = _add_news_pages(news, search_query, date_from,
                                   date_to, [1], news_per_page)
    query_time = (datetime.now() - start_time).total_seconds()
    logger.debug(f'got first page of news, count={len(news)}')

    n_pages_total = math.ceil(n_news_total / news_per_page)
    n_queries_planned = _get_planned_queries_count(query_time, n_pages_total)
    logger.debug(
        'n_news_total={}, n_pages_total={}, n_queries_planned={}'.format(
            n_news_total, n_pages_total, n_queries_planned)
    )

    page_numbers = _get_random_page_numbers(n_pages_total, n_queries_planned)
    logger.debug(f'getting pages of news={page_numbers}')

    _add_news_pages(news, search_query, date_from,
                    date_to, page_numbers, news_per_page)
    logger.info(f'got all pages of news, count={len(news)}')

    return news


def _add_news_pages(news: list[dict], search_query: str, date_from: str,
                    date_to: str, page_numbers: Iterable[int], news_per_page: int) -> int:
    """
    Adds news from each page to news list

    :param news: news list
    :type news: list[dict]
    :param search_query: query to search
    :type search_query: str
    :param date_from: start date in format 2000-01-01T00:00:00
    :type date_from: str
    :param date_to: end date in format 2000-01-01T00:00:00
    :type date_to: str
    :param page_numbers: page numbers to get
    :type page_numbers: Iterable[int]
    :param news_per_page: news per page, must be between 10 and 50
    :type news_per_page: int
    :return: total news count for the query
    :rtype: int
    """
    total_count = 0
    for i_page in page_numbers:
        page = _get_news_page(search_query, i_page,
                              news_per_page, date_from, date_to)
        news_portion = get_json_value(page, ['value'])
        total_count += int(get_json_value(page, ['totalCount']))
        news.extend(news_portion if news_portion is not None else [])

    return total_count


def _get_news_page(search_query: str, page_number: int, page_size: int,
                   date_from: str, date_to: str) -> list[dict]:
    """
    Gets a news page using WebSearch API

    :param text: query to search
    :type text: str
    :param page_number: page number, must be greater than 0
    :type page_number: int
    :param page_size: news per page, must be between 10 and 50
    :type page_size: int
    :param date_from: start date in format 2000-01-01T00:00:00
    :type date_from: str
    :param date_to: end date in format 2000-01-01T00:00:00
    :type date_to: str
    :raise ValueError: raised when search query is empty
    :raise ValueError: raised when date is invalid
    :raise ValueError: raised when page_number or page_size is out of range
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: news
    :rtype: list[dict]
    """
    if search_query.strip() == '':
        raise ValueError('Search query must not be empty')

    if page_number <= 0:
        raise ValueError('Page number must be greater than 0')

    if not 10 <= page_size <= 50:
        raise ValueError('Page size must be between 10 and 50')

    if not datetime_valid(date_from) or not datetime_valid(date_to):
        raise ValueError('Invalid date format')

    url = 'https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI'

    request = {
        'q': search_query,
        'pageNumber': page_number,
        'pageSize': page_size,
        'autoCorrect': 'true',
        'fromPublishedDate': date_from,  # '2023-04-03T00:00:00',
        'toPublishedDate': date_to,  # '2023-04-09T23:59:59'
    }

    headers = {
        'X-RapidAPI-Key': config.RAPID_API_KEY,
        'X-RapidAPI-Host': 'contextualwebsearch-websearch-v1.p.rapidapi.com'
    }

    response = api_request('GET', url, headers=headers, request=request)

    return response


def datetime_valid(date: str) -> bool:
    """
    Validates a date. Correct format is 2000-01-01T00:00:00

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


def _get_planned_queries_count(query_time: float, n_pages_total: int) -> int:
    """
    Gets the number of queries planned to be sent

    :param query_time: time of a single query
    :type query_time: float
    :param n_pages_total: total number of pages
    :type n_pages_total: int
    :return: number of queries planned to be sent
    :rtype: int
    """
    query_sleep_time = 100
    max_queries_time = 6

    n_queries_planned = math.floor(
        (max_queries_time + query_sleep_time) / (query_time + query_sleep_time))
    n_queries_planned = min(n_queries_planned, n_pages_total)

    return n_queries_planned


def _get_random_page_numbers(n_pages_total: int, n_chunks: int) -> list[int]:
    """
    Generates random page number for each chunk

    :n_pages_total: number of pages
    :type n_pages_total: int
    :n_chunks: number of chunks
    :type n_chunks: int
    :raise ValueError: raised if number of pages is less or equal to zero
    :raise ValueError: raised if number of chunks is less or equal to zero
    :return: random page numbers
    :rtype: list[int]
    """
    if n_pages_total <= 0:
        raise ValueError('Number of pages must be greater than zero')

    if n_chunks < 0:
        raise ValueError('Number of chunks must be greater or equal to zero')

    page_numbers = []

    if n_chunks == 0:
        return page_numbers

    for i_chunk in range(n_chunks):
        chunk_size = n_pages_total / n_chunks
        i_beg = round(chunk_size * i_chunk) + 1
        i_end = round(chunk_size * (i_chunk + 1))
        page_numbers.append(randint(i_beg, i_end))

    return page_numbers


# TODO: remove
def main() -> None:
    search_query = 'ecology'
    date_from = '2023-04-03T00:00:00'
    date_to = '2023-04-09T23:59:59'
    summary_key = 'description'

    news = get_news(search_query, date_from, date_to)

    summary_input = get_summary_input(news, summary_key)
    redis_cache.cache_summary_input(
        search_query, date_from, date_to, summary_input)

    most_important_news = order_news_by_importance(news)
    redis_cache.cache_most_important_news(search_query, date_from,
                                          date_to, most_important_news)
