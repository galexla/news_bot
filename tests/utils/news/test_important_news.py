import os
from unittest.mock import patch

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from tests.test_utils import load_news_from_dir
    from utils.news.important_news import get_important_news


def test_get_important_news() -> None:
    """
    Tests get_important_news function
    """
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    news = load_news_from_dir(data_dir)
    important_news = get_important_news('', news, 'description')

    actual = {id: news_item['importance']
              for id, news_item in important_news.items()}

    assert actual['6718760237732508493'] == 8
    assert actual['809070968785199941'] == 31
    assert actual['7720720362422410409'] == 13
    assert actual['5083624909196031876'] == 21
    assert actual['4408843533799644020'] == 23
    assert actual['6049394458971597468'] == 30
    assert actual['5641607859976004885'] == 11
    assert actual['2046649311940024345'] == 3
