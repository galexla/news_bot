from datetime import datetime
from time import sleep
from typing import Any

import loguru
import requests
from loguru import logger


class ApiQuery:
    """
    API query
    """

    def __init__(self, method: str, url: str, headers: dict, request: dict,
                 interval: int, timeout: int = 10):
        """
        Constructor

        :param method: method type (POST or GET)
        :type method: str
        :param url: API url
        :type url: str
        :param headers: request headers
        :type headers: dict
        :param request: request itself
        :type request: dict
        :param interval: interval between queries
        :type interval: int
        :param timeout: request timeout
        :type timeout: int
        """
        self.method = method.upper()
        if self.method not in ('POST', 'GET'):
            raise ValueError('Method must be POST or GET')
        self.url = url
        self.headers = headers
        self.request = request
        self.interval = interval
        self.timeout = timeout
        self.start_time = None
        self.end_time = None

    def execute(self) -> Any:
        """
        Executes the query

        :return: result of the query
        :rtype: Any
        """
        logger.debug(f'Sending request to {self.url}')

        try:
            if self.method == 'POST':
                response = requests.request(
                    self.method, self.url, json=self.request,
                    headers=self.headers, timeout=self.timeout)
            else:
                response = requests.request(
                    self.method, self.url, headers=self.headers,
                    params=self.request, timeout=self.timeout)

            if response.status_code == requests.codes.ok:
                logger.success('Got answer({}) from {} , answer={}'.format(
                    len(response.text), self.url, response.text[:100]))
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    logger.error('JSON decoding failed')
            else:
                logger.error(f'Got status code {response.status_code}')
        except requests.RequestException:
            logger.error('Request failed')

        return None


class ApiQueryScheduler:
    """
    API query scheduler

    Args:
        from_start (bool): whether to calculate time from a query start or from its end
        __current_query (ApiQuery): current query
    """
    from_start: bool = True
    __current_query: ApiQuery = None

    @classmethod
    def __get_sleep_time(cls, query: ApiQuery) -> int:
        """
        Returns the sleep time for a query

        :param query: query
        :type query: ApiQuery
        :return: sleep time
        :rtype: int
        """
        if query is None:
            return 0

        if cls.from_start:
            if query.start_time is None:
                return 0
            else:
                time_diff = datetime.utcnow() - query.start_time
                sleep_time = query.interval - time_diff.total_seconds()
                return max(0, sleep_time)
        else:
            if query.end_time is None:
                return 0
            else:
                time_diff = datetime.utcnow() - query.end_time
                sleep_time = query.interval - time_diff.total_seconds()
                return max(0, sleep_time)

    @classmethod
    def execute(cls, query: ApiQuery) -> Any:
        """
        Executes query

        :param query: query
        :type query: ApiQuery
        :return: result of the query
        :rtype: Any
        """
        sleep_time = cls.__get_sleep_time(cls.__current_query)
        if sleep_time > 0:
            loguru.debug(f'Sleeping for {sleep_time} seconds')
            sleep(sleep_time)

        query.start_time = datetime.utcnow()
        result = query.execute()
        query.end_time = datetime.utcnow()

        cls.__current_query = query
        return result
