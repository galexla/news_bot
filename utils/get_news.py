from typing import Optional

from config_data import config
from utils.misc import api_request, get_json_value


def get_news(search_query: str, date_from: str, date_to: str) -> Optional[str]:
    """
    Gets news using Web search API

    :param text: text
    :type text: str
    :param n_characters: number of characters in summary
    :type n_characters: int
    :return: text summary
    :rtype: Optional[str]
    """
    if search_query.strip() == '':
        return {}

    return _news_api_request(search_query, page_number=1, page_size=50,
                             date_from=date_from, date_to=date_to)


def _news_api_request(search_query: str, page_number: int, page_size: int, date_from: str, date_to: str) -> Optional[dict]:
    """
    Makes API request to Web search API to get news

    :param text: text
    :type text: str
    :param percent: size of the summary
    :type percent: float
    :return: text summary
    :rtype: Optional[str]
    """
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
        'X-RapidAPI-Key': config.NEWS_API_KEY,
        'X-RapidAPI-Host': 'contextualwebsearch-websearch-v1.p.rapidapi.com'
    }

    response = api_request('POST', url, headers=headers, request=request)
    # return get_json_value(response, ['summary'])
    return response
