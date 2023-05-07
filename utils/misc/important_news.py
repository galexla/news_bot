from typing import Iterable

from utils.misc.important_words import get_important_words, get_words


def order_news_by_importance(news: list[dict], text_keys: str | Iterable) -> list[dict]:
    """
    Gets most important news

    :param news: news
    :type news: list[dict]
    :return: most important news
    :rtype: list[dict]
    """
    if not news or not text_keys:
        return []

    important_news = {}
    important_words = get_important_words(news, text_keys)

    for news_item in news:
        important_news[news_item['id']] = {'importance': 0, 'news': news_item}
        all_words = get_words(news_item, text_keys)
        for word, importance in important_words.items():
            if word in all_words:
                important_news[news_item['id']]['importance'] += importance

        important_news[news_item['id']]['importance'] /= len(all_words)

    important_news = sorted(important_news.items(),
                            key=lambda x: x[1]['importance'], reverse=True)

    return dict(important_news)