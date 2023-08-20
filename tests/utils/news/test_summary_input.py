import os
from unittest.mock import patch

import pytest

from tests.test_utils import load_news_from_file

with patch('database.init_db.init_db'), patch(
    'database.init_db.create_tables'
):
    from utils.news.summary_input import (
        _clean_news_text,
        _get_average_length,
        _get_unique_news,
        _join_news,
        get_summary_input,
    )


def test__clean_news_text():
    """
    Tests _clean_news_text function
    """
    beg = ' \n\r\t'
    end = ' \n\r\t:;,-‐‑‒﹣－'
    assert _clean_news_text('') == '.'
    assert _clean_news_text('...') == '...'
    assert _clean_news_text('abc…') == 'abc…'
    assert _clean_news_text('asd') == 'asd.'
    assert _clean_news_text('asd.') == 'asd.'
    assert _clean_news_text('asd!') == 'asd!'
    assert _clean_news_text(beg + 'asd?' + end) == 'asd?'
    assert _clean_news_text(beg + 'asd' + end) == 'asd.'


def test__join_news():
    """
    Tests _join_news function
    """
    news = [
        {'text': 'te1'},
        {'text': 'tex2'},
        {'text': 'text3'},
        {'text': 'tex4'},
    ]
    assert (
        _join_news(news, 'text', 8) == 'te1.\n\ntex2.\n\ntext3.\n\ntex4.\n\n'
    )
    assert _join_news(news, 'text', 7) == 'te1.\n\ntex2.\n\ntex4.\n\n'
    assert _join_news(news, 'text', 6) == 'te1.\n\n'
    assert _join_news(news, 'text', 4) == ''
    assert _join_news([], 'text', 8) == ''
    pytest.raises(KeyError, _join_news, news, '', 8)


def test__get_average_length():
    news = [{'text': 'text1'}, {'text': 'text123'}, {'text': 'text12345'}]
    assert _get_average_length(news, 'text') == 7

    with pytest.raises(ValueError):
        _get_average_length([], 'text')
    with pytest.raises(ValueError):
        _get_average_length(news, '')
    with pytest.raises(ValueError):
        _get_average_length([{'text': ''}, {'text': ''}, {'text': ''}], 'text')


@patch('utils.news.summary_input.UNIQUE_KEY', 'text')
def test__get_unique_news():
    news = [
        {'text': 'text1', 'description': '123'},
        {'text': 'text1:2', 'description': 'dfdsf'},
        {'text': 'text12345', 'description': 'text12345'},
    ]
    assert _get_unique_news(news) == [{'text': 'text1', 'description': '123'}]

    news = [
        {'text': 'text_two2', 'description': 'aaa'},
        {'text': 'text_two', 'description': '1'},
        {'text': 'text12345', 'description': 'text123'},
    ]
    assert _get_unique_news(news) == [
        {'text': 'text_two2', 'description': 'aaa'},
        {'text': 'text12345', 'description': 'text123'},
    ]


def test_get_summary_input():
    file_name = os.path.join(
        os.path.dirname(__file__), 'data', 'news_ecology_20230403.json'
    )
    news = load_news_from_file(file_name)

    news_truncated = news[:10]
    actual = get_summary_input(news_truncated, 'description')
    with open(
        'tests/utils/news/data/10_news_summary_input.txt',
        'r',
        encoding='utf-8',
    ) as f:
        excepted = f.read()
    assert actual == excepted

    news_truncated = news[:60]
    actual = get_summary_input(news_truncated, 'description')
    with open(
        'tests/utils/news/data/60_news_summary_input.txt',
        'r',
        encoding='utf-8',
    ) as f:
        excepted = f.read()
    assert actual == excepted
