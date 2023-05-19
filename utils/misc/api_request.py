import datetime
import time

import requests
from loguru import logger


def api_request(method_type: str, url: str, headers: dict, request: dict,
                timeout: int = 10, retry_on_too_many: bool = True,
                max_retry_delay: int = 1) -> dict:
    """
    Returns the result of a request

    :param method_type: method type (POST or GET)
    :type method_type: str
    :param url: url
    :type url: str
    :param headers: request headers
    :type headers: dict
    :param request: request itself
    :type request: dict
    :param timeout: request timeout
    :type timeout: int
    :param retry_on_too_many: retry if status code is 429 (too many requests)?
    :type retry_on_too_many: bool
    :param max_retry_delay: maximum sleep time before retrying
    :type max_retry_delay: int
    :raise ValueError: raised if method_type is not POST or GET
    :raise ValueError: raised if retry_on_too_many is less than zero
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: result of the request
    :rtype: Optional[dict]
    """
    method_type = method_type.upper()
    if method_type not in ('POST', 'GET'):
        raise ValueError('method_type must be POST or GET')

    if retry_on_too_many < 0:
        raise ValueError('retry_on_too_many must be >= 0')

    logger.debug(f'Sending request to {url}')

    try:
        if method_type == 'POST':
            response = requests.request(
                'POST', url, json=request, headers=headers, timeout=timeout)
        else:
            response = requests.request(
                'GET', url, headers=headers, params=request, timeout=timeout)

        if response.status_code == requests.codes.ok:
            logger.success('Got answer({}) from {} , answer={}'.format(
                len(response.text), url, response.text[:100]))

            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as exception:
                logger.exception(exception)

                raise exception
        else:
            if retry_on_too_many and response.status_code == requests.codes.too_many:
                logger.warning(
                    f'Request returned status code {response.status_code}, retrying')
                retry_time = _get_retry_delay(response)
                if retry_time <= max_retry_delay:
                    time.sleep(retry_time)

                    return api_request(method_type, url, headers,
                                       request, timeout, False)

            exception = requests.RequestException(
                f'Request returned status code {response.status_code}')
            logger.exception(exception)

            raise exception
    except requests.RequestException as exception:
        logger.exception(exception)

        raise exception


def _get_retry_delay(response: requests.Response) -> int:
    """
    Returns the delay before retrying

    :param response: response
    :type response: requests.Response
    :return: delay before retrying
    :rtype: int
    """
    retry_time = response.headers.get('Retry-After')
    if retry_time is None:
        return 1
    elif retry_time.isdigit():
        return int(retry_time)
    else:
        # Retry-After is a date
        retry_date = datetime.strptime(retry_time, "%a, %d %b %Y %H:%M:%S %Z")
        return (retry_date - datetime.now()).total_seconds()
