import re
from collections import Counter
from typing import Iterable

import wordfreq


def get_important_words(news: list[dict], text_keys: str | Iterable, words_percent: int = 25) -> dict:
    """
    Gets most important words from news

    :param news: news
    :type news: list[dict]
    :param text_keys: keys to get text from news
    :type text_keys: str | Iterable
    :param words_percent: percent of words to get
    :type words_percent: int
    :return: dictionary with most important words
    :rtype: dict
    """
    all_words = get_all_words(news, text_keys)
    important_words = _get_words_importance(all_words)

    important_words = sorted(important_words.items(),
                             key=lambda item: item[1], reverse=True)

    n_words = len(important_words)
    max_words = int(n_words * words_percent / 100)
    important_words = dict(important_words[:max_words])

    return important_words


def get_all_words(news: list[dict], text_keys: str | Iterable) -> list[str]:
    """
    Gets all words from news

    :param news: news
    :type news: list[dict]
    :param text_keys: keys to get text from news
    :type text_keys: str | Iterable
    :return: all words
    :rtype: list[str]
    """
    if isinstance(text_keys, str):
        text_keys = [text_keys]

    all_words = []

    for news_item in news:
        words = get_words(news_item, text_keys)
        all_words.extend(words)

    return all_words


def get_words(news_item: dict, text_keys: str | Iterable) -> list[str]:
    """
    Gets words from news item

    :param news_item: news item
    :type news_item: dict
    :return: words
    :rtype: list[str]
    """
    if isinstance(text_keys, str):
        text_keys = [text_keys]

    all_words = []

    for text_key in text_keys:
        text = news_item.get(text_key, '').strip()
        if len(text) > 0:
            words = _re_get_words(text)
            all_words.extend(words)

    return all_words


def _re_get_words(text: str) -> list[str]:
    """
    Gets words from text

    :param text: text
    :type text: str
    :return: words
    :rtype: list[str]
    """
    return re.findall(r'\w+', text.lower())


def _get_words_importance(all_words: list[str]) -> dict[str, float]:
    """
    Gets importance of words

    :param all_words: all words
    :type all_words: list[str]
    :return: dictionary with importance of words
    :rtype: dict[str, float]
    """
    important_words = {}
    if len(all_words) == 0:
        return important_words

    n_words = len(all_words)
    counter = Counter(all_words)

    for word, count in counter.items():
        if word in important_words:
            continue

        frequency = count / n_words
        usual_frequency = wordfreq.word_frequency(
            word, 'en', wordlist='best', minimum=0.0)
        importance = frequency / usual_frequency if usual_frequency != 0 else -10

        important_words[word] = importance

    max_importance = max(important_words.values(), key=lambda x: x)
    max_importance = max(max_importance, 1)
    for word in important_words.keys():
        if important_words[word] == -10:
            important_words[word] = max_importance * 0.9

    return important_words
