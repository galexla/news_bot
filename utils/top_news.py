from datetime import date
from typing import Tuple

from utils.misc import redis_cache as cache
from utils.news.tf_idf import most_similar_news_ids
from utils.news.utils import important_news_to_texts


def get_top_news(sentences: list[str], important_news: dict[dict]) -> list[dict]:
    """
    Tries to get top 5 news from GPT-3 chatbot. In case of failure
    gets it from top 10 of most important news

    :param important_news: news in format {id: {importance: float, news: dict}, ...}
    :type important_news: dict[dict]
    :return: top 5 news
    :rtype: list[dict]
    """
    text_keys = ('title', 'description', 'body')
    news_texts = important_news_to_texts(important_news, text_keys)
    ids = most_similar_news_ids(sentences, news_texts)
    top_news = []
    for _, news_id in ids.items():
        top_news.append(important_news[news_id]['news'])

    return top_news


def cache_top_news(top_news: list[dict], date_to: date) -> None:
    """
    Caches top news

    :param top_news: top news
    :type top_news: list[dict]
    :rtype: None
    """
    for news_item in top_news:
        key = cache.key('top_news_item', news_item['id'])
        if not cache.exists(key):
            cache.set(key, news_item, ex=cache.get_ttl(date_to))


def get_cached_top_news(id: str) -> Tuple[str, str, str, int]:
    """
    Returns top news item title, url, body and ttl

    :param id: news id
    :type id: str
    :return: title and url
    :rtype: Tuple[str, str, str, int]
    """
    key = cache.key('top_news_item', id)
    if cache.exists(key):
        news_item = cache.get(key)
        return news_item, cache.ttl(key)
    return '', '', '', 0
