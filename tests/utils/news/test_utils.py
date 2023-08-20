from datetime import date
from unittest.mock import patch

with patch('database.init_db.init_db'), patch(
    'database.init_db.create_tables'
):
    from utils.news import utils as news_utils


def test_get_first_day_of_week() -> None:
    """
    Tests get_first_day_of_week
    """
    date1 = date(2020, 1, 1)
    assert news_utils.get_first_day_of_week(date1) == date(2019, 12, 30)

    date1 = date(2020, 1, 5)
    assert news_utils.get_first_day_of_week(date1) == date(2019, 12, 30)

    date1 = date(2020, 1, 6)
    assert news_utils.get_first_day_of_week(date1) == date(2020, 1, 6)


def test_get_last_day_of_week() -> None:
    """
    Tests get_last_day_of_week
    """
    date1 = date(2019, 12, 27)
    assert news_utils.get_last_day_of_week(date1) == date(2019, 12, 29)

    date1 = date(2019, 12, 30)
    assert news_utils.get_last_day_of_week(date1) == date(2020, 1, 5)

    date1 = date(2020, 1, 6)
    assert news_utils.get_last_day_of_week(date1) == date(2020, 1, 12)


def test_to_text() -> None:
    """
    Tests to_text
    """
    news_item = {}
    text_keys = []
    assert news_utils.to_text(news_item, text_keys) == ''

    news_item = {
        'title': 'title',
        'text': 'text',
        'url': 'url',
        'date': 'date',
        'source': 'source',
        'tags': 'tags',
        'important': 'important',
    }
    text_keys = ['title', 'text']
    assert news_utils.to_text(news_item, text_keys) == 'title\n\ntext'


def test_news_to_texts() -> None:
    """
    Tests news_to_texts
    """
    news = []
    text_keys = []
    assert list(news_utils.news_to_texts(news, text_keys)) == []

    news = [
        {
            'title': 'title1',
            'text': 'text1',
            'url': 'url1',
            'date': 'date1',
            'source': 'source1',
            'tags': 'tags1',
            'important': 'important1',
        },
        {
            'title': 'title2',
            'text': 'text2',
            'url': 'url2',
            'date': 'date2',
            'source': 'source2',
            'tags': 'tags2',
            'important': 'important2',
        },
    ]
    text_keys = ['title', 'text']
    assert list(news_utils.news_to_texts(news, text_keys)) == [
        'title1\n\ntext1',
        'title2\n\ntext2',
    ]


def test_important_news_to_texts() -> None:
    """
    Tests important_news_to_texts
    """
    news = {}
    text_keys = []
    assert news_utils.important_news_to_texts(news, text_keys) == {}

    news = {
        'id1': {
            'importance': 0.5,
            'news': {
                'title': 'title1',
                'text': 'text1',
                'url': 'url1',
                'date': 'date1',
                'source': 'source1',
                'tags': 'tags1',
                'important': 'important1',
            },
        },
        'id2': {
            'importance': 0.2,
            'news': {
                'title': 'title2',
                'text': 'text2',
                'url': 'url2',
                'date': 'date2',
                'source': 'source2',
                'tags': 'tags2',
                'important': 'important2',
            },
        },
    }
    text_keys = ['title', 'text']
    assert news_utils.important_news_to_texts(news, text_keys) == {
        'id1': 'title1\n\ntext1',
        'id2': 'title2\n\ntext2',
    }


def test_date_from_to_str() -> str:
    """
    Converts date_from to string
    """
    date_from = date(2020, 1, 1)
    expected = date_from.strftime('%Y-%m-%dT00:00:00')
    assert news_utils.date_from_to_str(date_from) == expected

    expected = date_from.strftime('%Y-%m-%d 00:00:00')
    assert news_utils.date_from_to_str(date_from, False) == expected


def test_date_to_to_str() -> str:
    """
    Converts date_to to string
    """
    date_to = date(2020, 1, 1)
    expected = date_to.strftime('%Y-%m-%dT23:59:59')
    assert news_utils.date_to_to_str(date_to) == expected

    expected = date_to.strftime('%Y-%m-%d 23:59:59')
    assert news_utils.date_to_to_str(date_to, False) == expected
