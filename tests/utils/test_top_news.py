from datetime import date
from unittest.mock import patch

with patch('database.init_db.init_db'), patch(
    'database.init_db.create_tables'
):
    from utils.top_news import (
        cache_top_news_items,
        get_cached_top_news_item,
        get_top_news,
    )


def test_get_top_news():
    sentences = []
    important_news = {
        'news_id1': {'news': 'news 1'},
        'news_id2': {'news': 'news 2'},
        'news_id3': {'news': 'news 3'},
        'news_id4': {'news': 'news 4'},
    }

    assert [item['news'] for item in important_news.values()][
        :3
    ] == get_top_news(sentences, important_news, 3)

    assert [item['news'] for item in important_news.values()][
        :1
    ] == get_top_news(sentences, important_news, 1)


@patch('utils.top_news.cache.key')
@patch('utils.top_news.cache.exists')
@patch('utils.top_news.cache.set')
@patch('utils.top_news.cache.calc_ttl')
def test_cache_top_news_items(mock_calc_ttl, mock_set, mock_exists, mock_key):
    top_news = [{'id': 1, 'news': 'news 1'}, {'id': 2, 'news': 'news 2'}]
    date_to = date.today()
    mock_key.return_value = 'key'
    mock_exists.return_value = False

    cache_top_news_items(top_news, date_to)

    mock_calc_ttl.assert_called_with(date_to)
    mock_calc_ttl.call_count == len(top_news)
    assert mock_set.call_count == len(top_news)


@patch('utils.top_news.cache.key')
@patch('utils.top_news.cache.exists')
@patch('utils.top_news.cache.get')
@patch('utils.top_news.cache.get_ttl')
def test_get_cached_top_news_exists(
    mock_get_ttl, mock_get, mock_exists, mock_key
):
    id = '1'
    mock_key.return_value = 'key'
    mock_exists.return_value = True
    mock_get.return_value = {'id': id, 'news': 'news 1'}
    mock_get_ttl.return_value = 100

    news_item, ttl = get_cached_top_news_item(id)

    assert news_item == {'id': id, 'news': 'news 1'}
    assert ttl == 100


@patch('utils.top_news.cache.key')
@patch('utils.top_news.cache.exists')
def test_get_cached_top_news_not_exists(mock_exists, mock_key):
    id = '1'
    mock_key.return_value = 'key'
    mock_exists.return_value = False

    news_item, ttl = get_cached_top_news_item(id)

    assert news_item is None
    assert ttl == 0
