from typing import Iterable

from config_data import config


def get_important_news(
    search_query: str, news: list[dict], text_keys: str | Iterable
) -> dict[dict]:
    """
    Returns most important news ordered by descending importance in format:
    {id: {importance: float, news: dict}, ...}

    :param search_query: a search string
    :type search_query: str
    :param news: news
    :type news: list[dict]
    :param text_keys: keys to get text from
    :type text_keys: str | Iterable[str]
    :return: most important news
    :rtype: dict[dict]
    """
    if not news or not text_keys:
        return []

    if isinstance(text_keys, str):
        text_keys = [text_keys]

    n_news = len(news)
    important_news = {}
    for i_item, news_item in enumerate(news):
        important_news[news_item[config.NEWS_ID]] = {
            'importance': n_news - i_item,
            'news': news_item,
        }

    return important_news
