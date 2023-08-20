from datetime import date
from unittest.mock import patch

import pytest

with patch('database.init_db.init_db'), patch(
    'database.init_db.create_tables'
):
    from utils.news import news


@pytest.mark.parametrize(
    'all_cache_exist, cache_exists, news_count, summary_input, important_news',
    [
        (
            True,
            True,
            1,
            'summary input',
            {'a': {'importance': 1}, 'b': {'importance': 2}},
        ),
        (
            True,
            True,
            5,
            'summary input 2',
            {'a': {'importance': 3}, 'b': {'importance': 4}},
        ),
        (
            False,
            True,
            5,
            'summary input 2',
            {'a': {'importance': 3}, 'b': {'importance': 4}},
        ),
        (
            False,
            False,
            5,
            'summary input 2',
            {'a': {'importance': 3}, 'b': {'importance': 4}},
        ),
        (False, False, 0, '', {}),
        (True, True, 0, '', {}),
    ],
)
@patch('utils.news.news.cache')
@patch('utils.news.news.news_api')
@patch('utils.news.news.get_important_news')
@patch('utils.news.news.get_summary_input')
def test_get_news_semimanufactures(
    mock_get_summary_input,
    mock_get_important_news,
    mock_news_api,
    mock_cache,
    all_cache_exist,
    cache_exists,
    news_count,
    summary_input,
    important_news,
):
    mock_cache.all_exist.return_value = all_cache_exist
    cache_get_values = {
        'news_count': news_count,
        'summary_input': summary_input,
        'important_news': important_news,
    }
    mock_cache.get.side_effect = lambda key: cache_get_values[
        key.split(':')[0]
    ]
    mock_cache.key_query.side_effect = lambda *args: args[0]
    mock_cache.exists.return_value = cache_exists
    mock_get_summary_input.return_value = summary_input
    mock_get_important_news.return_value = important_news
    mock_news_api.get_news.return_value = (important_news, news_count)

    (
        actual_news_count,
        actual_summary_input,
        actual_important_news,
    ) = news.get_news_semimanufactures(
        'Ecology', date(2020, 1, 1), date(2020, 1, 3)
    )

    if news_count == 0:
        assert actual_news_count == 0
        assert actual_summary_input == ''
        assert actual_important_news == {}
        return

    if not all_cache_exist:
        mock_news_api.get_news.assert_called_once_with(
            'Ecology', date(2020, 1, 1), date(2020, 1, 3)
        )
        mock_get_important_news.assert_called_once()
        if cache_exists:
            mock_get_summary_input.assert_not_called()
            assert mock_cache.set.call_count == 2
        else:
            mock_get_summary_input.assert_called_once()
            assert mock_cache.set.call_count == 3
    else:
        mock_news_api.get_news.assert_not_called()
        mock_get_important_news.assert_not_called()
        mock_get_summary_input.assert_not_called()
        mock_cache.set.assert_not_called()

    assert actual_news_count == news_count
    assert actual_summary_input == summary_input
    assert actual_important_news == important_news


def test_important_news_to_iterator():
    important_news = {'a': {'news': 'a'}, 'b': {'news': 'b'}}
    actual = news.important_news_to_iterator(important_news)
    assert list(actual) == ['a', 'b']

    important_news = {}
    actual = news.important_news_to_iterator(important_news)
    assert list(actual) == []
