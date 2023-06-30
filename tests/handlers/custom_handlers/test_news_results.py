from datetime import date
from unittest.mock import Mock, patch

import pytest

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from handlers.custom_handlers import news_results


@pytest.fixture
def mock_bot():
    return Mock()


@pytest.fixture
def chat_and_user_id():
    return 123, 321


@pytest.fixture
def date_range():
    return date(2022, 1, 1), date(2022, 1, 2)


@pytest.fixture
def important_news():
    return [{'id': 1, 'importance': 1, 'news': {'id': 1, 'title': 'title1'}},
            {'id': 2, 'importance': 2, 'news': {'id': 2, 'title': 'title2'}}]


@pytest.fixture
def top_news():
    return [{'id': 1, 'title': 'title1'}]


@patch('handlers.custom_handlers.news_results.get_news_semimanufactures')
@patch('handlers.custom_handlers.news_results._get_summary_and_top_news')
def test_get_results(get_summary_and_top_news_mock, get_news_semimanufactures_mock,
                     mock_bot, chat_and_user_id, date_range, important_news, top_news):
    get_news_semimanufactures_mock.return_value = (
        10, 'summary', important_news)
    get_summary_and_top_news_mock.return_value = ('summary', top_news)
    with patch('handlers.custom_handlers.news_results.bot', mock_bot):
        news_results.get_results(*chat_and_user_id, 'test_query', *date_range)
    assert get_news_semimanufactures_mock.call_count == 1
    assert get_summary_and_top_news_mock.call_count == 1
    assert mock_bot.set_state.call_count == 1
    assert mock_bot.delete_state.call_count == 1
    assert mock_bot.send_message.call_count == 4


@patch('utils.misc.redis_cache.redis_connection')
@patch('handlers.custom_handlers.news_results.get_summary', return_value='summary')
@patch('handlers.custom_handlers.news_results.get_top_news')
@patch('handlers.custom_handlers.news_results.cache_top_news')
def test_get_summary_and_top_news(
        cache_top_news_mock, get_top_news_mock, get_summary_mock,
        mock_redis_connection, date_range, top_news):
    mock_redis_connection.exists.return_value = False
    get_top_news_mock.return_value = top_news
    important_news = [{'id': 1, 'importance': 1, 'news': {'id': 1, 'title': 'title1'}},
                      {'id': 2, 'importance': 2, 'news': {'id': 2, 'title': 'title2'}}]
    result = news_results._get_summary_and_top_news(
        'test_query', *date_range, 'summary_input', important_news)
    assert get_summary_mock.call_count == 1
    assert get_top_news_mock.call_count == 1
    assert cache_top_news_mock.call_count == 1
    assert result == ('summary', [{'id': 1, 'title': 'title1'}])


def test_display_summary_and_top_news(mock_bot):
    with patch('handlers.custom_handlers.news_results.bot', mock_bot):
        news_results._display_summary_and_top_news(
            '123', ['summary1', 'summary2'], [{'id': 1, 'title': 'title2'}, {'id': 2, 'title': 'title2'}])
    assert mock_bot.send_message.call_count == 2
