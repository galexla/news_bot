import math
import time
from datetime import datetime
from random import randint
from typing import Iterable

from loguru import logger

from config_data import config
from utils.misc import api_request, get_json_value
from utils.news.utils import is_datetime_valid


def get_news(search_query: str, date_from: str, date_to: str) -> list[dict]:
    """
    Gets news using WebSearch API

    :param text: query to search
    :type text: str
    :param date_from: start date in format %Y-%m-%dT%H:%M:%S
    :type date_from: str
    :param date_to: end date in format %Y-%m-%dT%H:%M:%S
    :type date_to: str
    :raise ValueError: raised when search query is empty
    :raise ValueError: raised when date is invalid
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: news
    :rtype: list[dict]
    """
    news_per_page = 50
    query_sleep_time = 0.15

    news = []

    n_news_total, query_time = add_first_page_of_news(
        news, search_query, date_from, date_to, news_per_page, query_sleep_time)
    logger.debug(f'got first page of news, count={len(news)}')

    n_pages_total = math.ceil(n_news_total / news_per_page)
    n_queries_planned = _get_planned_queries_count(
        query_time, n_pages_total, query_sleep_time,
        max_total_time=6, max_queries=10)
    logger.debug(
        'n_news_total={}, n_pages_total={}, n_queries_planned={}'.format(
            n_news_total, n_pages_total, n_queries_planned)
    )

    page_numbers = _get_random_page_numbers(n_pages_total, n_queries_planned)

    _add_news(news, search_query, date_from, date_to,
              page_numbers, news_per_page, query_sleep_time)
    logger.info(f'got all pages of news, count={len(news)}')

    return news


def add_first_page_of_news(news: list[dict], search_query: str,
                           date_from: str, date_to: str, news_per_page: int,
                           query_sleep_time: float) -> tuple[int, float]:
    """
    Gets first page of news with API and adds it to news list

    :param news: news list
    :type news: list[dict]
    :param search_query: query to search
    :type search_query: str
    :param date_from: start date in format %Y-%m-%dT%H:%M:%S
    :type date_from: str
    :param date_to: end date in format %Y-%m-%dT%H:%M:%S
    :type date_to: str
    :param news_per_page: number of news per page
    :type news_per_page: int
    :param query_sleep_time: time to sleep between queries
    :type query_sleep_time: float
    :raise ValueError: raised when search query is empty
    :raise ValueError: raised when date is invalid
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: total news count for the query and query time
    :rtype: tuple[int, float]
    """
    start_time = datetime.now()
    n_news_total = _add_news(news, search_query, date_from,
                             date_to, [1], news_per_page, query_sleep_time)
    query_time = (datetime.now() - start_time).total_seconds()

    return n_news_total, query_time


def _add_news(news: list[dict], search_query: str, date_from: str, date_to: str,
              page_numbers: Iterable[int], news_per_page: int, sleep_time: float) -> int:
    """
    Gets news with API and adds it to news list

    :param news: news list
    :type news: list[dict]
    :param search_query: query to search
    :type search_query: str
    :param date_from: start date in format %Y-%m-%dT%H:%M:%S
    :type date_from: str
    :param date_to: end date in format %Y-%m-%dT%H:%M:%S
    :type date_to: str
    :param page_numbers: page numbers to get
    :type page_numbers: Iterable[int]
    :param news_per_page: news per page, must be between 10 and 50
    :type news_per_page: int
    :param sleep_time: time to sleep between queries, in seconds
    :type sleep_time: float
    :raise ValueError: raised when search query is empty
    :raise ValueError: raised when date is invalid
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
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
        time.sleep(sleep_time)

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
    :param date_from: start date in format %Y-%m-%dT%H:%M:%S
    :type date_from: str
    :param date_to: end date in format %Y-%m-%dT%H:%M:%S
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

    if not is_datetime_valid(date_from) or not is_datetime_valid(date_to):
        raise ValueError('Invalid date format')

    url = 'https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI'

    request = {
        'q': search_query,
        'pageNumber': page_number,
        'pageSize': page_size,
        'autoCorrect': 'true',
        'fromPublishedDate': date_from,
        'toPublishedDate': date_to,
    }

    headers = {
        'X-RapidAPI-Key': config.RAPID_API_KEY,
        'X-RapidAPI-Host': 'contextualwebsearch-websearch-v1.p.rapidapi.com'
    }

    response = api_request('GET', url, headers=headers, request=request)

    return response


def _get_planned_queries_count(query_time: float, n_pages_total: int,
                               sleep_time: float, max_total_time: float = 6,
                               max_queries: int = 10) -> int:
    """
    Gets the number of queries planned to be sent

    :param query_time: time of a single query
    :type query_time: float
    :param n_pages_total: total number of pages
    :type n_pages_total: int
    :param sleep_time: time to sleep between queries, in seconds
    :type sleep_time: float
    :param max_total_time: maximum execution time of all queries, in seconds
    :type max_total_time: float
    :param max_queries: maximum number of queries to send
    :type max_queries: int
    :return: number of queries planned to be sent
    :rtype: int
    """
    n_queries_planned = math.floor(
        (max_total_time + sleep_time) / (query_time + sleep_time))
    n_queries_planned = min(n_queries_planned, max_queries)
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
