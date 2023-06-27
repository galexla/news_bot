from datetime import datetime
from time import sleep
from typing import Any

import loguru
import requests
from loguru import logger


class ApiQuery:
    """
    Query to API

    Args:
        method (str): method type (must be POST or GET)
        url (str): API url
        headers (dict): request headers
        body (dict): request body
        interval (int): interval between queries
        timeout (int): request timeout

    Attributes:
        interval (int): interval between queries
        start_time (datetime or None): query start time, None until request is made
        end_time (datetime or None): query end time, None until request is made
        _method (str): method type (POST or GET)
        _url (str): API url
        _headers (dict): request headers
        _body (dict): request body if method is POST, else request params
        _timeout (int): request timeout

    Raises:
        ValueError: if method is not POST or GET
    """

    def __init__(self, method: str, url: str, headers: dict, body: dict,
                 interval: int, timeout: int = 10):
        self._method = method.upper()
        if self._method not in ('POST', 'GET'):
            raise ValueError('Method must be POST or GET')
        self._url = url
        self._headers = headers
        self._body = body
        self._interval = interval
        self._timeout = timeout
        self._start_time = None
        self._end_time = None

    @property
    def interval(self) -> int:
        """
        Interval between queries

        :return: interval between queries
        :rtype: int
        """
        return self._interval

    @property
    def start_time(self) -> datetime:
        """
        Query start time

        :return: start time
        :rtype: datetime
        """
        return self._start_time

    @start_time.setter
    def start_time(self, value: datetime) -> None:
        """
        Sets query start time

        :param value: value
        :type value: datetime
        :rtype: None
        """
        self._start_time = value

    @property
    def end_time(self) -> datetime:
        """
        Query end time

        :return: end time
        :rtype: datetime
        """
        return self._end_time

    @end_time.setter
    def end_time(self, value: datetime) -> None:
        """
        Sets query end time

        :param value: value
        :type value: datetime
        :rtype: None
        """
        self._end_time = value

    def execute(self) -> Any:
        """
        Executes the query

        :return: result of the query
        :rtype: Any
        """
        logger.debug(f'Sending request to {self._url}')

        try:
            if self._method == 'POST':
                response = requests.request(
                    self._method, self._url, json=self._body,
                    headers=self._headers, timeout=self._timeout)
            else:
                response = requests.request(
                    self._method, self._url, headers=self._headers,
                    params=self._body, timeout=self._timeout)

            if response.status_code == requests.codes.ok:
                logger.success('Got answer({}) from {} , answer={}'.format(
                    len(response.text), self._url, response.text[:100]))
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

    Attributes:
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
