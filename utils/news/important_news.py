import re
from typing import Iterable

import numpy as np

from config_data import config
from loader import freq_word_vectors


def get_important_news(search_query: str, news: list[dict],
                       text_keys: str | Iterable) -> dict[dict]:
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
    query_avg_vector = get_text_avg_vector(search_query, freq_word_vectors)

    for news_item in news:
        item_text = join_key_values(news_item, text_keys)
        item_avg_vector = get_text_avg_vector(item_text, freq_word_vectors)
        important_news[news_item[config.NEWS_ID]] = {
            'importance': get_similarity(query_avg_vector, item_avg_vector),
            'news': news_item
        }
    important_news = sorted(important_news.items(),
                            key=lambda item: item[1]['importance'], reverse=True)
    important_news = dict(important_news)

    return important_news


def get_average_vector(vectors: Iterable[np.ndarray]) -> np.ndarray:
    if len(vectors) == 0:
        return None
    elif len(vectors) == 1:
        return vectors[0]
    vectors = np.vstack(list(vectors))
    return np.mean(vectors, axis=0)


def words_to_vectors(words: Iterable[str], word_vectors: dict) -> Iterable[np.ndarray]:
    for word in words:
        if word in word_vectors:
            yield word_vectors[word]


def get_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
    return float(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2)))


def get_words(text: str) -> list[str]:
    """
    Gets words from a text

    :param text: text
    :type text: str
    :return: words
    :rtype: list[str]
    """
    if len(text) > 0:
        return re.findall(r'[\w\-]+', text)
    return []


def get_text_avg_vector(text: str, top_words: dict) -> list:
    text = text.lower()
    text_words = get_words(text)
    text_vectors = list(words_to_vectors(text_words, top_words))
    text_avg_vector = get_average_vector(text_vectors)

    return text_avg_vector


def join_key_values(dictionary: dict, keys: tuple, sep: str = '\n') -> str:
    texts = (str(dictionary[key])
             for key in keys if dictionary[key] is not None)
    text = sep.join(texts)

    return text
