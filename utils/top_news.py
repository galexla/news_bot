import random
import re
from typing import Iterable, Iterator

import requests
from loguru import logger

from utils.misc import send_chatgpt_request
from utils.misc.json_value import get_json_value


def get_top_news(important_news: dict[dict]) -> list[dict]:
    """
    Gets top 5 news from GPT-3 chatbot

    :param important_news: news in format: {id: {importance: float, news: dict}, ...}
    :type important_news: dict[dict]
    :return: top 5 news
    :rtype: list[dict]
    """
    news_count = 50
    news_count = min(news_count, len(important_news))
    random_ids = random.sample(list(important_news.keys()), news_count)
    random_news = (important_news[id]['news'] for id in random_ids)

    news_text = _news_to_text(random_news)
    chatgpt_prompt = _get_chatgpt_prompt(news_text)

    try:
        response = send_chatgpt_request(chatgpt_prompt)
        response_text = get_json_value(
            response, ['choices', 0, 'message', 'content'])
        top_news = _decode_chatgpt_answer(response_text)

        top_news_ids = (news['id'] for news in top_news)
        news = get_news_by_ids(top_news_ids, important_news)
    except (requests.RequestException,
            requests.exceptions.JSONDecodeError) as exception:
        logger.exception(exception)

        top_news_ids = get_top_news_ids_simple(important_news)
        news = get_news_by_ids(top_news_ids, important_news)

    return news


def get_random_news(important_news: dict[dict], count: int) -> list[dict]:
    """
    Gets random news from important news

    :param important_news: news in format: {id: {importance: float, news: dict}, ...}
    :type important_news: dict[dict]
    :param count: count of news
    :type count: int
    :return: random news
    """
    random_ids = random.sample(list(important_news.keys()), count)
    random_news = [important_news[id]['news'] for id in random_ids]

    return random_news


def _news_to_text(news: Iterable[dict], text_key: str = 'title') -> str:
    """
    Converts news to text in format: id\ntitle\n\nid\ntitle...

    :param news: news
    :type news: Iterable[dict]
    :param text_key: key of text in news
    :type text_key: str
    :return: text in format: id\ntitle\n\nid\ntitle...
    :rtype: str
    """
    text = ''
    for news_item in news:
        text += f'{news_item["id"]}\n{news_item[text_key]}\n\n'

    return text


def _get_chatgpt_prompt(news: str) -> str:
    """
    Gets prompt for GPT-3 chatbot from news string

    :param news: multiline string with news in format: id\ntitle\n\nid\ntitle...
    :type news: str
    :return: multiline string with prompt for GPT-3
    """
    return f'''Here are some news in format:

id1
title1

id2
title2

...

Can you choose 5 most important of them and provide the answer in the following format?

id1
title1

id2
title2

...


{news}
'''


def _decode_chatgpt_answer(answer: str) -> list[dict]:
    """
    Decodes answer from GPT-3 chatbot

    :param answer: answer from GPT-3 chatbot
    :type answer: str
    :return: list of news
    :rtype: list[dict]
    """
    answer += '\n\n'
    regex_pattern = r'(\d+)\n(.+?)\n\n'
    found = re.findall(regex_pattern, answer)

    news = []
    for item in found:
        news.append({
            'id': item[0],
            'title': item[1]
        })

    return news


def get_news_by_ids(ids: Iterable[str],
                    most_important_news: dict[dict]) -> list[dict]:
    """
    Gets news by ids

    :param ids: ids
    :type ids: Iterable[str]
    :param most_important_news: most important news
    :type most_important_news: dict[dict]
    :return: news
    :rtype: list[dict]
    """
    return [most_important_news[id]['news'] for id in ids]


def get_top_news_ids_simple(most_important_news: dict[dict]) -> Iterator[str]:
    """
    Gets top news if GPT-3 request failed

    :param most_important_news: most important news
    :type most_important_news: dict[dict]
    :return: news ids
    :rtype: Iterator[str]
    """
    if len(most_important_news) < 8:
        indexes = (1, 2, 3, 5, 8)
    else:
        indexes = tuple(range(1, 6))

    max_i = max(indexes)
    i = 1
    for id in most_important_news.keys():
        if i in indexes:
            i += 1
            yield id
        if i > max_i:
            break
