from typing import Optional

from config_data import config
from utils.misc import api_request, get_json_value


def get_summary(text: str, n_characters: int = 500) -> Optional[str]:
    """
    Gets text summary using Text-analysis12 API

    :param text: text
    :type text: str
    :param n_characters: number of characters in summary
    :type n_characters: int
    :return: text summary
    :rtype: Optional[str]
    """
    if len(text) <= n_characters:
        return text

    percent = round(n_characters / len(text) * 100, 2)
    return _summary_api_request(text, percent)


def _summary_api_request(text: str, percent: float) -> Optional[dict]:
    """
    Make API request to Text-analysis12 API to get text summary

    :param text: text
    :type text: str
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
        'text': text
    }

    response = api_request('POST', url, headers, request)
    return get_json_value(response, ['summary'])
