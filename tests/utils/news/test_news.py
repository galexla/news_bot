from datetime import date
from unittest.mock import MagicMock, patch

import pytest

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from utils.news import news


def test_get_news_count():
    assert news.get_news_count(None) == 0
    assert news.get_news_count([]) == 0
    assert news.get_news_count([{}]) == 1
    assert news.get_news_count([{}, {}]) == 2


def cache_get_set(key, ttl, func, *args, **kwargs):
    return func(*args, **kwargs)


@pytest.fixture
def mock_cache():
    with patch('utils.news.news.cache', new_callable=MagicMock) as mock:
        yield mock


@pytest.fixture
def mock_important_news():
    with patch('utils.news.news.get_important_news', new_callable=MagicMock) as mock:
        yield mock


@pytest.fixture
def mock_summary_input():
    with patch('utils.news.news.get_summary_input', new_callable=MagicMock) as mock:
        yield mock


@pytest.fixture
def mock_news_count():
    with patch('utils.news.news.get_news_count', new_callable=MagicMock) as mock:
        yield mock


@pytest.fixture
def mock_get_news():
    with patch('utils.news.news_api.get_news', new_callable=MagicMock) as mock:
        yield mock


@pytest.fixture
def mock_key_query():
    with patch('utils.news.news.cache.key_query', new_callable=MagicMock) as mock:
        yield mock


@pytest.mark.parametrize('all_cache_exist, news_count, summary_input, important_news', [
    (True, 1, 'summary input', {
     'a': {'importance': 1}, 'b': {'importance': 2}}),
    (True, 5, 'summary input 2', {
     'a': {'importance': 3}, 'b': {'importance': 4}}),
    (False, 5, 'summary input 2', {
     'a': {'importance': 3}, 'b': {'importance': 4}})
])
def test_get_news_semimanufactures(all_cache_exist, news_count, summary_input, important_news,
                                   mock_cache, mock_important_news, mock_summary_input,
                                   mock_news_count, mock_get_news, mock_key_query):
    mock_cache.all_exist.return_value = all_cache_exist
    mock_cache.get_set.side_effect = cache_get_set
    mock_news_count.return_value = news_count
    mock_summary_input.return_value = summary_input
    mock_important_news.return_value = important_news
    mock_key_query.side_effect = lambda *args: args[0]

    actual = news.get_news_semimanufactures(
        'Ecology', date(2020, 1, 1), date(2020, 1, 3))

    if not all_cache_exist:
        mock_get_news.assert_called_once()
    else:
        mock_get_news.assert_not_called()

    assert actual == (news_count, summary_input, important_news)
    assert mock_cache.get_set.call_count == 3
    assert mock_news_count.call_count == 1
    assert mock_summary_input.call_count == 1
    assert mock_important_news.call_count == 1

    arg1_expected = ('news_count', 'summary_input', 'important_news')
    for i, args in enumerate(mock_cache.get_set.call_args_list):
        assert args[0][0] == arg1_expected[i]
