import math
import re
from collections import Counter
from typing import Iterable
import wordfreq


def get_important_words(texts: Iterable[str] | str, words_percent: int = 25) -> dict:
    """
    Gets most important words from news

    :param texts: texts
    :type texts: str | Iterable
    :param words_percent: percent of words to get
    :type words_percent: int
    :return: dictionary with most important words
    :rtype: dict
    """
    if isinstance(texts, str):
        texts = [texts]

    all_words = get_all_words(texts)
    important_words = _get_words_importance(all_words)

    important_words = sorted(important_words.items(),
                             key=lambda item: item[1], reverse=True)

    n_words = len(important_words)
    max_words = int(n_words * words_percent / 100)
    important_words = dict(important_words[:max_words])

    return important_words


def get_all_words(texts: Iterable[str]) -> list[str]:
    """
    Gets all words from news

    :param texts: keys to get text from news
    :type texts: Iterable[str]
    :return: all words
    :rtype: list[str]
    """
    all_words = []

    for text in texts:
        words = get_words(text)
        all_words.extend(words)

    return all_words


def get_words(text: str) -> list[str]:
    """
    Gets words from news item

    :param text: text
    :type text: str
    :return: words
    :rtype: list[str]
    """
    text = text.strip()
    if len(text) > 0:
        return _re_get_words(text)

    return []


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

    minus_inf = float('-inf')
    for word, count in counter.items():
        if word in important_words:
            continue

        frequency = count / n_words
        usual_frequency = wordfreq.word_frequency(
            word, 'en', wordlist='best', minimum=0.0)
        importance = math.log2(
            frequency / usual_frequency) if usual_frequency != 0 else minus_inf

        important_words[word] = importance

    # max_importance = max(important_words.values())
    # max_importance = max(max_importance, 1)
    # for word in important_words.keys():
    #     if important_words[word] == minus_inf:
    #         important_words[word] = max_importance * 0.4

    importances = sorted(important_words.values(), reverse=True)
    importances_of_unknown = importances[3] * 0.7
    for word in important_words.keys():
        if important_words[word] == minus_inf:
            important_words[word] = importances_of_unknown

    return important_words
