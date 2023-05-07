import json
import os
import re

from utils.misc.important_news import order_news_by_importance


def test_order_news_by_importance() -> None:
    """
    Tests get_important_news function
    """
    dir = '/home/alexander/_dev/educ/skillbox/python_basic_diploma_exprm/news/api/NewsSearchAPI/russia_2023_0401-0407/'
    news = load_news_from_dir(dir)
    news_index = create_news_index(news)

    filename = dir + 'joined_text/news_text_descr.txt'
    with open(filename, 'r') as file:
        text = file.read()

    important_news = order_news_by_importance(news, 'description')
    important_news = tuple(important_news.items())

    expected = {
        0: 'Chinas Xi Jinping expressed',
        70: 'Lukashenko: NATO',
        105: 'The battle in Bakhmut',
        175: 'Canadiens right winger',
        280: 'American and European',
        315: 'MOSCOW  Longtime'
    }

    for i, text in expected.items():
        id = important_news[i][0]
        assert news_index[id]['description'].startswith(text)


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
        if re.match(r'^\d+.json$', filename):
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
        text = file.read()
        news_item = json.loads(text)
        return news_item['value']


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
        news_index[news_item['id']] = news_item

    return news_index
