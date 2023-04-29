import re
from datetime import datetime
from typing import Optional

from config_data import config
from utils.misc import api_request, get_json_value


def get_news(search_query: str, page_number: int, page_size: int, date_from: str, date_to: str) -> Optional[dict]:
    """
    Gets news using WebSearch API

    :param text: query to search
    :type text: str
    :param page_number: page number
    :type page_number: int
    :param page_size: news per page
    :type page_size: int
    :param date_from: start date in format 2000-01-01T00:00:00
    :type date_from: str
    :param date_to: end date in format 2000-01-01T00:00:00
    :type date_to: str
    :raise ValueError: raised when search query is empty or date is invalid
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: news
    :rtype: Optional[dict]
    """
    if search_query.strip() == '':
        raise ValueError('Search query must not be empty')

    page_number = max(page_number, 1)
    page_size = min(max(page_size, 10), 50)

    if not datetime_valid(date_from) or not datetime_valid(date_to):
        raise ValueError('Invalid date format')

    url = 'https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI'

    request = {
        'q': search_query,
        'pageNumber': page_number,
        'pageSize': page_size,
        'autoCorrect': 'true',
        'fromPublishedDate': date_from,  # '2023-04-01T00:00:00',
        'toPublishedDate': date_to,  # '2023-04-07T23:59:59'
    }

    headers = {
        'X-RapidAPI-Key': config.RAPID_API_KEY,
        'X-RapidAPI-Host': 'contextualwebsearch-websearch-v1.p.rapidapi.com'
    }

    response = api_request('GET', url, headers=headers, request=request)
    # return get_json_value(response, ['summary'])
    return response


def datetime_valid(date: str) -> bool:
    try:
        datetime.fromisoformat(date)
    except:
        return False

    return re.match(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$', date)
