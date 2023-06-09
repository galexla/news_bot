import math
from collections import Counter

from utils.news.important_words import get_words


def most_similar_news_ids(sentences: list[str],
                          news_texts: dict[str, str]) -> dict[str, dict]:
    """
    Gets most similar news item for each sentence

    :param sentences: sentences
    :type sentences: list[str]
    :param news_texts: news texts in format {news_id: text}
    :type news_texts: dict[str, str]
    :raise TypeError: if sentences is not of type list
    :return: similarities in format {sentence: news_id}
    :rtype: dict[str, dict]
    """
    if not isinstance(sentences, list):
        raise TypeError('sentences must be of type list.')

    tf_idf = get_tf_idf(news_texts)
    similarities = get_similarities(sentences, news_texts, tf_idf)

    chosen_news_ids = set()
    result = {}
    for sentence, news_similarities in similarities.items():
        news_similarities = sorted(news_similarities.items(),
                                   key=lambda x: x[1], reverse=True)
        for i in range(len(news_similarities)):
            news_id = news_similarities[i][0]
            if news_id not in chosen_news_ids:
                result[sentence] = news_id
                chosen_news_ids.add(news_id)
                break

    return result


def get_tf_idf(news_texts: dict[str, str]) -> dict[str, dict]:
    """
    Gets tf-idf fo each word in each news text

    :param news_texts: news texts in format {news_id: text}
    :type news_texts: dict[str, str]
    :return: tf-idf in format {news_id: {word: tf-idf}}
    :rtype: dict[str, dict]
    """
    all_words = set()
    news = {}
    for news_id, text in news_texts.items():
        words = get_words(text)
        news[news_id] = {}
        news[news_id]['counter'] = Counter(words)
        n_words = len(words)
        news[news_id]['freq'] = {word: count / n_words
                                 for word, count in news[news_id]['counter'].items()}
        news[news_id]['words'] = set(words)
        all_words.update(news[news_id]['words'])

    word_in_news_count = {}
    for word in all_words:
        word_in_news_count[word] = 0
        for news_id, news_item in news.items():
            if word in news_item['words']:
                word_in_news_count[word] += 1

    idf = {}
    n_texts = len(news_texts)
    for word, count in word_in_news_count.items():
        idf[word] = math.log(n_texts / count)

    tf_idf = {}
    for news_id in news.keys():
        words = news[news_id]['words']
        tf_idf[news_id] = {}
        for word in words:
            tf_idf[news_id][word] = news[news_id]['freq'][word] * idf[word]

    return tf_idf


def get_similarities(sentences: list[str], news_texts: dict[str, str],
                     tf_idf: dict[str, str]) -> dict[str, dict]:
    """
    Gets similarities between sentences and news texts

    :param sentences: sentences
    :type sentences: list[str]
    :param news_texts: news texts in format {news_id: text}
    :type news_texts: dict[str, str]
    :param tf_idf: tf-idf
    :type tf_idf: dict[str, str]
    :return: similarities in format {sentence: {news_id: similarity}}
    :rtype: dict[str, dict]
    """
    similarities = {}
    for sentence in sentences:
        sentence_words = get_words(sentence)
        similarities.setdefault(sentence, {})
        for news_id, words in news_texts.items():
            news_words = get_words(words)
            common_words = set(sentence_words) & set(news_words)
            similarity = 0
            for word in common_words:
                similarity += tf_idf[news_id][word]
            similarities[sentence][news_id] = similarity

    return similarities
