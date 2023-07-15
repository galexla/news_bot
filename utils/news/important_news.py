from typing import Iterable
from config_data import config

from utils.news.important_words import get_important_words, get_words
from utils.news.utils import news_to_texts, to_text


def get_important_news(news: list[dict], text_keys: str | Iterable) -> dict[dict]:
    """
    Returns most important news ordered by descending importance in format:
    {id: {importance: float, news: dict}, ...}

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

    important_news = {}
    news_texts = news_to_texts(news, text_keys)
    important_words = get_important_words(news_texts)

    for news_item in news:
        important_news[news_item[config.NEWS_ID]] = {
            'importance': 0, 'news': news_item}
        text = to_text(news_item, text_keys)
        text_words = get_words(text)
        n_text_words = len(text_words)

        text_words = set(text_words)
        words_to_walk = text_words.intersection(set(important_words.keys()))
        for word in words_to_walk:
            importance = important_words[word]
            important_news[news_item[config.NEWS_ID]
                           ]['importance'] += importance

        important_news[news_item[config.NEWS_ID]]['importance'] /= n_text_words

    important_news = sorted(important_news.items(),
                            key=lambda x: x[1]['importance'], reverse=True)

    return dict(important_news)
