from typing import Optional

from config_data import config
from utils.misc import api_request, get_json_value, redis_cache


def get_summary(search_query: str, datetime_from: str,
                datetime_to: str) -> Optional[str]:
    summary_text = redis_cache.get_summary(
        search_query, datetime_from, datetime_to)

    if summary_text:
        return summary_text
    else:
        summary_input = redis_cache.get_summary_input(
            search_query, datetime_from, datetime_to)
        if summary_input:
            summary_text = _get_summary(summary_input)
            if summary_text:
                redis_cache.set_summary(
                    search_query, datetime_from, datetime_to, summary_text)
                return summary_text

    return None


def _get_summary(summary_input: str, n_characters: int = 500) -> Optional[str]:
    """
    Gets text summary using Text-analysis12 API

    :param text: text
    :type text: str
    :param n_characters: number of characters in summary
    :type n_characters: int
    :return: text summary
    :rtype: Optional[str]
    """
    if len(summary_input) <= n_characters:
        return summary_input

    percent = round(n_characters / len(summary_input) * 100, 2)
    return _summary_api_request(summary_input, percent)


def _summary_api_request(summary_input: str, percent: float) -> Optional[dict]:
    """
    Make API request to Text-analysis12 API to get text summary

    :param summary_input: text
    :type summary_input: str
    :param percent: size of the summary
    :type percent: float
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: text summary
    :rtype: Optional[str]
    """
    percent = min(100, percent)

    url = 'https://text-analysis12.p.rapidapi.com/summarize-text/api/v1.1'

    headers = {
        'content-type': 'application/json',
        'X-RapidAPI-Key': config.RAPID_API_KEY,
        'X-RapidAPI-Host': 'text-analysis12.p.rapidapi.com'
    }

    request = {
        'language': 'english',
        'summary_percent': percent,
        'text': summary_input
    }

    response = api_request('POST', url, headers, request)
    return get_json_value(response, ['summary'])
