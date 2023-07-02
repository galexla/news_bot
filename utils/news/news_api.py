import math
from datetime import date, datetime
from random import randint
from typing import Iterable

from loguru import logger

from config_data import config
from utils.misc import get_json_value
from utils.misc.api_query_scheduler import ApiQuery, ApiQueryScheduler
from utils.news.utils import date_from_to_str, date_to_to_str

MIN_REQUEST_INTERVAL = 1
MAX_TOTAL_QUERIES_TIME = 6
NEWS_PER_PAGE = 50
MAX_QUERIES_COUNT = 7
MIN_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50


def get_news(search_query: str, date_from: date, date_to: date) -> list[dict]:
    """
    Gets news using WebSearch API

    :param search_query: query to search
    :type search_query: str
    :param date_from: start date
    :type date_from: date
    :param date_to: end date
    :type date_to: date
    :raises ValueError: raised when search query is empty
    :raises requests.RequestException: raised if the request fails
    :raises requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: news
    :rtype: list[dict]
    """
    news = []

    n_news_total, query_time = add_first_page_of_news(
        news, search_query, date_from, date_to, NEWS_PER_PAGE)
    logger.debug(f'got first page of news, count={len(news)}')

    n_pages_total = math.ceil(n_news_total / NEWS_PER_PAGE)
    n_queries_planned = _get_planned_queries_count(
        query_time, n_pages_total, MAX_TOTAL_QUERIES_TIME, MAX_QUERIES_COUNT)
    logger.debug(
        'n_news_total={}, n_pages_total={}, n_queries_planned={}'.format(
            n_news_total, n_pages_total, n_queries_planned)
    )

    page_numbers = _get_random_page_numbers(n_pages_total, n_queries_planned)

    _add_news(news, search_query, date_from, date_to,
              page_numbers, NEWS_PER_PAGE)
    logger.info(f'got all pages of news, count={len(news)}')

    return news


def _get_planned_queries_count(query_time: float, n_pages_total: int,
                               max_total_time: float, max_queries_count: int) -> int:
    """
    Gets the number of queries planned to be sent

    :param query_time: expected time of a single query
    :type query_time: float
    :param n_pages_total: total number of pages
    :type n_pages_total: int
    :param max_total_time: maximum time to spend on queries
    :type max_total_time: float
    :param max_queries_count: maximum number of queries to send
    :type max_queries_count: int
    :raises ValueError: raised when any of the arguments is less than or equal to 0
    :return: number of queries planned to be sent
    :rtype: int
    """
    if query_time <= 0 or n_pages_total <= 0 \
            or max_total_time <= 0 or max_queries_count <= 0:
        raise ValueError('Arguments must be greater than 0')

    n_queries_planned = math.floor(max_total_time / query_time)
    n_queries_planned = min(n_queries_planned, max_queries_count)
    n_queries_planned = min(n_queries_planned, n_pages_total)
    n_queries_planned = max(n_queries_planned, 1)

    return n_queries_planned


def add_first_page_of_news(news: list[dict], search_query: str,
                           date_from: date, date_to: date,
                           news_per_page: int) -> tuple[int, float]:
    """
    Gets first page of news with API and adds it to news list

    :param news: news list
    :type news: list[dict]
    :param search_query: query to search
    :type search_query: str
    :param date_from: start date
    :type date_from: date
    :param date_to: end date
    :type date_to: date
    :param news_per_page: number of news per page
    :type news_per_page: int
    :return: total news count for the query and query time
    :rtype: tuple[int, float]
    """
    start_time = datetime.now()
    n_news_total = _add_news(
        news, search_query, date_from, date_to, [1], news_per_page)
    query_time = (datetime.now() - start_time).total_seconds()
    query_time = max(query_time, MIN_REQUEST_INTERVAL)

    return n_news_total, query_time


def _add_news(news: list[dict], search_query: str, date_from: date, date_to: date,
              page_numbers: Iterable[int], news_per_page: int) -> int:
    """
    Gets news with API and adds it to news list

    :param news: news list
    :type news: list[dict]
    :param search_query: query to search
    :type search_query: str
    :param date_from: start date
    :type date_from: date
    :param date_to: end date
    :type date_to: date
    :param page_numbers: page numbers to get
    :type page_numbers: Iterable[int]
    :param news_per_page: news per page, must be between 10 and 50
    :type news_per_page: int
    :return: total news count for the query
    :rtype: int
    """
    total_count = 0
    for i_page in page_numbers:
        page = _get_news_page(
            search_query, i_page, news_per_page, date_from, date_to)
        news_portion = get_json_value(page, ['value'])
        total_count += int(get_json_value(page, ['totalCount']))
        news.extend(news_portion if news_portion is not None else [])

    return total_count


def _get_news_page(search_query: str, page_number: int, page_size: int,
                   date_from: date, date_to: date) -> list[dict]:
    """
    Gets a news page using WebSearch API

    :param search_query: query to search
    :type search_query: str
    :param page_number: page number, must be greater than 0
    :type page_number: int
    :param page_size: news per page, must be between 10 and 50
    :type page_size: int
    :param date_from: start date
    :type date_from: date
    :param date_to: end date
    :type date_to: date
    :raises ValueError: raised when search query is empty
    :raises ValueError: raised when page_number or page_size is out of range
    :raises requests.RequestException: raised if the request fails
    :raises requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: news
    :rtype: list[dict]
    """
    if search_query.strip() == '':
        raise ValueError('Search query must not be empty')

    if page_number <= 0:
        raise ValueError('Page number must be greater than 0')

    if not MIN_PAGE_SIZE <= page_size <= MAX_PAGE_SIZE:
        raise ValueError(
            f'Page size must be between {MIN_PAGE_SIZE} and {MAX_PAGE_SIZE}')

    datetime_from = date_from_to_str(date_from)
    datetime_to = date_to_to_str(date_to)

    url = 'https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI'

    request = {
        'q': search_query,
        'pageNumber': page_number,
        'pageSize': page_size,
        'autoCorrect': 'true',
        'fromPublishedDate': datetime_from,
        'toPublishedDate': datetime_to,
    }

    headers = {
        'X-RapidAPI-Key': config.RAPID_API_KEY,
        'X-RapidAPI-Host': 'contextualwebsearch-websearch-v1.p.rapidapi.com'
    }

    query = ApiQuery('GET', url, headers=headers,
                     request=request, interval=MIN_REQUEST_INTERVAL)
    response = ApiQueryScheduler.execute(query)

    return response


def _get_random_page_numbers(n_pages_total: int, n_chunks: int) -> list[int]:
    """
    Generates random page number for each chunk

    :param n_pages_total: number of pages
    :type n_pages_total: int
    :param n_chunks: number of chunks
    :type n_chunks: int
    :raises ValueError: raised if number of pages is less or equal to zero
    :raises ValueError: raised if number of chunks is less or equal to zero
    :return: random page numbers
    :rtype: list[int]
    """
    if n_pages_total <= 0:
        raise ValueError('Number of pages must be greater than zero')

    if n_chunks <= 0:
        raise ValueError('Number of chunks must be greater than zero')

    page_numbers = []

    if n_chunks == 0:
        return page_numbers

    for i_chunk in range(n_chunks):
        chunk_size = n_pages_total / n_chunks
        i_beg = round(chunk_size * i_chunk) + 1
        i_end = round(chunk_size * (i_chunk + 1))
        page_numbers.append(randint(i_beg, i_end))

    return page_numbers
