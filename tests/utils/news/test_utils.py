from datetime import date

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
    assert news_utils.to_text(news_item, text_keys) == 'title\ntext'


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
        'title1\ntext1',
        'title2\ntext2',
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
        'id2': {
            'title': 'title2',
            'text': 'text2',
            'url': 'url2',
            'date': 'date2',
            'source': 'source2',
            'tags': 'tags2',
            'important': 'important2',
        },
    }
    text_keys = ['title', 'text']
    assert news_utils.important_news_to_texts(news, text_keys) == {
        'id1': 'title1\ntext1',
        'id2': 'title2\ntext2',
    }