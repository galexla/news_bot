from typing import Optional

from config_data import config
from utils.misc import api_request, get_json_value


def get_summary(text: str, n_characters: int = 500) -> Optional[list]:
    """
    Gets text summary using Text-analysis12 API

    :param text: text
    :type text: str
    :param n_characters: maximum size of the summary
    :type n_characters: int
    :return: sentences of the summary
    :rtype: Optional[list]
    """
    n_characters = max(0, n_characters)
    if len(text) <= n_characters:
        return text

    percent = round(n_characters / len(text) * 100, 3)
    return get_summary_percent(text, percent)


def get_summary_percent(text: str, percent: float) -> Optional[list]:
    """
    Make API request to Text-analysis12 API to get text summary

    :param summary_input: text
    :type summary_input: str
    :param percent: size of the summary
    :type percent: float
    :raise requests.RequestException: raised if the request fails
    :raise requests.exceptions.JSONDecodeError: raised if JSON decoding fails
    :return: sentences of the summary
    :rtype: Optional[list]
    """
    percent = min(100, percent)
    percent = max(0, percent)

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
    sentences = get_json_value(response, ['sentences'])

    return sentences
