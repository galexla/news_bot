import json
import os
import re

from utils.news.important_news import get_important_news


def test_get_important_news() -> None:
    """
    Tests get_important_news function
    """
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    news = load_news_from_dir(data_dir)

    important_news = get_important_news(news, 'description')
    importances = {id: news_item['importance']
                  for id, news_item in important_news.items()}
    expected = {'4457673410068488150': 3.0439041727906697, '3232520032701218817': 2.417731550438876, '6049394458971597468': 2.413940006697732, '3270947201236837767': 2.290515401601123, '4408843533799644020': 2.0862144148542696, '2952168276410620286': 1.8776178903753242, '8211796118481681273': 1.8483051828026753, '4255870151932984461': 1.827241032946209, '7720720362422410409': 1.820345601135945, '979025652461928862': 1.7969705476892164, '6718760237732508493': 1.746048702181373, '1906259068725363965': 1.7312877074564692, '5083624909196031876': 1.6192766723136742, '6681247523478043470': 1.4838134119525217, '7719313014531830067': 1.4738660436739355, '2046649311940024345': 1.4586465473663675,
                '5641607859976004885': 1.4408524827577407, '1066348599423775721': 1.3851924442235959, '9073108373000108053': 1.3208435458468686, '1816134593642589133': 1.2561836006870486, '8965383178459808462': 1.252986417285364, '8081595657655941016': 1.2238372416702892, '5897938562860003904': 1.159750873493518, '6205571237385168549': 1.095566923317859, '2547606122880455985': 1.0631314467545212, '809070968785199941': 1.0547239871472225, '8013334774008502268': 0.9677618295641398, '129251292489994149': 0.9135275193075572, '6831006204920480013': 0.7583937061658947, '6023222182896830417': 0.7549286105867181, '2498842934204653860': 0.6626862331044493, '6473208710660374843': 0.5500729466908321}
    assert importances == expected


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