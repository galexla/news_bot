from loguru import logger
import requests


def api_request(method_type: str, url: str, headers: dict, request: dict, timeout: int = 10) -> dict:
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
    :return: result of the request
    :rtype: Optional[dict]
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    """
    method_type = method_type.upper()
    if method_type not in ('POST', 'GET'):
        return None

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
                len(response.text), url, response.text[:60]))

            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as exception:
                logger.exception(exception)
                raise exception
        else:
            exception = requests.RequestException(
                f'Request returned status code {response.status_code}')
            logger.exception(exception)
            raise exception
    except requests.RequestException as exception:
        logger.exception(exception)
        raise exception
