import json
import os
import re

from config_data import config


def load_news_from_dir(dirname: str) -> list[dict]:
    """
    Loads news from json files in directory

    :param dirname: directory with json files
    :type dirname: str
    :return: list of news
    :rtype: list[dict]
    """
    news = []
    for filename in os.listdir(dirname):
        if re.match(r'^news_.+.json$', filename):
            filename = os.path.join(dirname, filename)
            news_item = load_news_from_file(filename)
            news.extend(news_item)

    return news


def load_news_from_file(filename: str) -> list[dict]:
    """
    Loads news from json file

    :param filename: json file
    :type filename: str
    :return: list of news
    :rtype: list[dict]
    """
    with open(filename, 'r') as file:
        news = json.load(file)
        for item in news['value']:
            item[config.NEWS_BODY] = item.pop('body', '')
        return news.pop('value', [])


def create_news_index(news: list[dict]) -> dict:
    """
    Creates index of news by id

    :param news: list of news
    :type news: list[dict]
    :return: index of news by id
    :rtype: dict
    """
    news_index = {}
    for news_item in news:
        news_index[news_item[config.NEWS_ID]] = news_item

    return news_index
