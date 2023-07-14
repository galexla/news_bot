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
PAGE_SIZE = 100
# TODO: change to 2 for manual testing
MAX_QUERIES_COUNT = 7
# MAX_QUERIES_COUNT = 2
MIN_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


def get_news(search_query: str, date_from: date, date_to: date) -> list[dict]:
    """
    Gets news using WebSearch API

    :param search_query: query to search
    :type search_query: str
    :param date_from: start date
    :type date_from: date
    :param date_to: end date
    :type date_to: date
    :raises ValueError: raised when search query is empty or any other parameter is invalid in subsequent calls
    :return: news
    :rtype: list[dict]
    """
    news = []

    n_news_total, query_time = add_first_page_of_news(
        news, search_query, date_from, date_to, PAGE_SIZE)
    n_pages_total = math.ceil(n_news_total / PAGE_SIZE)
    logger.success(f'got first page of news, count={len(news)}'
                   f', total={n_news_total}, total_pages={n_pages_total}')

    n_queries = _get_queries_count(
        query_time, n_pages_total, MAX_TOTAL_QUERIES_TIME, MAX_QUERIES_COUNT)
    logger.debug('planned {} more queries'.format(n_queries - 1))

    if n_queries > 1:
        page_numbers = _get_random_page_numbers(
            start_chunk=1, n_pages_total=n_pages_total, n_chunks=n_queries)

        _add_news(news, search_query, date_from, date_to,
                  page_numbers, PAGE_SIZE)
        logger.success(f'got rest of pages, news count={len(news)}')

    return news


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


def _get_queries_count(query_time: float, n_pages_total: int,
                       max_queries_time: float, max_queries_count: int) -> int:
    """
    Gets total number of queries planned to be sent (first page included)

    :param query_time: expected time of a single query
    :type query_time: float
    :param n_pages_total: total number of pages
    :type n_pages_total: int
    :param max_queries_time: maximum time to spend on queries
    :type max_queries_time: float
    :param max_queries_count: maximum number of queries to send
    :type max_queries_count: int
    :return: number of queries planned to be sent
    :rtype: int
    """
    if n_pages_total <= 0 or max_queries_time <= 0 or max_queries_count <= 0:
        return 0

    if query_time <= 0:
        query_time = MIN_REQUEST_INTERVAL

    n_queries_planned = math.floor(max_queries_time / query_time)
    n_queries_planned = min(n_queries_planned, max_queries_count)
    n_queries_planned = min(n_queries_planned, n_pages_total)

    return n_queries_planned


def _get_random_page_numbers(start_chunk: int, n_pages_total: int, n_chunks: int) -> list[int]:
    """
    Generates random page number for each chunk

    :param start_chunk: number of first chunk
    :type start_chunk: int
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

    for i_chunk in range(start_chunk, n_chunks):
        chunk_size = n_pages_total / n_chunks
        i_beg = round(chunk_size * i_chunk) + 1
        i_end = round(chunk_size * (i_chunk + 1))
        page_numbers.append(randint(i_beg, i_end))

    return page_numbers


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
    JSON_NEWS_PATH = ['news']
    JSON_TOTAL_COUNT_PATH = ['available']
    total_count = 0
    for i_page in page_numbers:
        page = _get_news_page(
            search_query, i_page, news_per_page, date_from, date_to)
        news_portion = get_json_value(page, JSON_NEWS_PATH)
        total_count += int(get_json_value(page, JSON_TOTAL_COUNT_PATH))
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
    :raises ValueError: raised when search query is less than 3 characters long
    :raises ValueError: raised when page_number is less than 1
    :raises ValueError: raised when page_size is out of [10, 100] range
    :raises ValueError: raised when request failed
    :return: news
    :rtype: list[dict]
    """
    if len(search_query.strip()) < 3:
        raise ValueError('Search query must be at least 3 characters long')

    if page_number <= 0:
        raise ValueError('Page number must be greater than 0')

    if not MIN_PAGE_SIZE <= page_size <= MAX_PAGE_SIZE:
        raise ValueError(
            f'Page size must be between {MIN_PAGE_SIZE} and {MAX_PAGE_SIZE}')

    datetime_from = date_from_to_str(date_from, False)
    datetime_to = date_to_to_str(date_to, False)
    offset = (page_number - 1) * page_size

    url = 'https://api.worldnewsapi.com/search-news'

    request = {
        'api-key': config.NEWS_API_KEY,
        'text': search_query,
        'language': 'en',
        'earliest-publish-date': datetime_from,
        'latest-publish-date': datetime_to,
        'sort': 'publish-time',
        'sort-direction': 'DESC',
        'offset': offset,
        'number': page_size
    }

    # Free worldnewsapi.com API query can sometimes execute for 60 seconds
    # and sometimes only 3. That's why we try 2 times with 10 seconds timeout.
    # for _ in range(2):
    #     interval = randint(400, 1000) / 100
    #     timeout = randint(7, 10)
    #     query = ApiQuery('GET', url, headers=None, body=request,
    #                      interval=interval, timeout=timeout)
    #     response = ApiQueryScheduler.execute(query)
    #     if response is not None:
    #         break
    query = ApiQuery('GET', url, headers=None, body=request,
                        interval=MIN_REQUEST_INTERVAL, timeout=10)
    response = ApiQueryScheduler.execute(query)

    if response is None:
        raise ValueError(
            f'Request {search_query} from {datetime_from} to {datetime_to} failed')

    return response
