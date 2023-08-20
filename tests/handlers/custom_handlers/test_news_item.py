from unittest.mock import patch

import pytest
from telebot.types import CallbackQuery, Chat, Message, User

with patch('database.init_db.init_db'), patch(
    'database.init_db.create_tables'
):
    from handlers.custom_handlers.news_item import (
        bot_click_news_item,
        bot_news_summary,
    )


@pytest.fixture
def message():
    user = User(1, False, first_name='test_user')
    message = Message(1, user, 0, Chat(1, 'private'), '', {}, '{}')
    message.text = '/news_1'
    return message


@pytest.fixture
def callback_query():
    user = User(1, False, first_name='test_user')
    message = Message(1, user, 0, Chat(1, 'private'), '', {}, '{}')
    query = CallbackQuery(
        '1',
        user,
        data='news_123',
        chat_instance='private',
        json_string='{}',
        message=message,
    )
    return query


@pytest.fixture
def callback_query2():
    user = User(1, False, first_name='test_user')
    message = Message(1, user, 0, Chat(1, 'private'), '', {}, '{}')
    query = CallbackQuery(
        '1',
        user,
        data='summary_1',
        chat_instance='private',
        json_string='{}',
        message=message,
    )
    return query


@pytest.fixture
def news_item():
    return {
        'id': '123',
        'title': 'test title',
        'url': 'test_url',
        'content': 'test body',
    }


@patch('handlers.custom_handlers.news_item.bot')
@patch('handlers.custom_handlers.news_item.top_news')
def test_bot_click_news_item(
    mock_top_news, mock_bot, news_item, callback_query
):
    mock_top_news.get_cached_top_news_item.return_value = (news_item, 3600)

    bot_click_news_item(callback_query)

    mock_top_news.get_cached_top_news_item.assert_called_once()
    assert (
        mock_top_news.get_cached_top_news_item.call_args[0][0]
        == news_item['id']
    )

    mock_bot.send_message.assert_called_once()
    assert (
        mock_bot.send_message.call_args[0][0] == callback_query.message.chat.id
    )
    assert mock_bot.send_message.call_args[0][1] == f'*{news_item["title"]}*'
    assert mock_bot.send_message.call_args[1]['parse_mode'] == 'Markdown'
    assert mock_bot.send_message.call_args[1]['reply_markup'] is not None


@patch('handlers.custom_handlers.news_item.bot')
@patch('handlers.custom_handlers.news_item.top_news')
def test_bot_click_news_item_error(
    mock_top_news, mock_bot, news_item, callback_query
):
    mock_top_news.get_cached_top_news_item.return_value = (None, 0)

    bot_click_news_item(callback_query)

    mock_top_news.get_cached_top_news_item.assert_called_once()
    assert (
        mock_top_news.get_cached_top_news_item.call_args[0][0]
        == news_item['id']
    )

    mock_bot.send_message.assert_called_once()
    assert (
        mock_bot.send_message.call_args[0][0] == callback_query.message.chat.id
    )
    assert mock_bot.send_message.call_args[0][1] == '*Some error occurred.*'
    assert mock_bot.send_message.call_args[1]['parse_mode'] == 'Markdown'


@patch('handlers.custom_handlers.news_item.bot')
@patch('handlers.custom_handlers.news_item.top_news')
@patch('handlers.custom_handlers.news_item.cache')
@patch('handlers.custom_handlers.news_item.get_summary')
def test_bot_news_summary(
    mock_get_summary,
    mock_cache,
    mock_top_news,
    mock_bot,
    news_item,
    callback_query2,
):
    mock_top_news.get_cached_top_news_item.return_value = (news_item, 3600)
    mock_cache.get_set.return_value = ['summary of article']
    mock_get_summary.return_value = 'summary of article'

    bot_news_summary(callback_query2)

    mock_bot.send_message.assert_called_once()
    assert (
        mock_bot.send_message.call_args[0][0]
        == callback_query2.message.chat.id
    )
    assert 'summary of article' in mock_bot.send_message.call_args[0][1]
    assert mock_bot.send_message.call_args[1]['parse_mode'] == 'Markdown'


@patch('handlers.custom_handlers.news_item.bot')
@patch('handlers.custom_handlers.news_item.top_news')
@patch('handlers.custom_handlers.news_item.cache')
@patch('handlers.custom_handlers.news_item.get_summary')
def test_bot_news_summary_error(
    mock_get_summary,
    mock_cache,
    mock_top_news,
    mock_bot,
    news_item,
    callback_query2,
):
    mock_top_news.get_cached_top_news_item.return_value = (None, 0)
    mock_cache.get_set.return_value = []
    mock_get_summary.return_value = 'summary of article'

    bot_news_summary(callback_query2)

    mock_bot.send_message.assert_called_once()
    assert (
        mock_bot.send_message.call_args[0][0]
        == callback_query2.message.chat.id
    )
    assert (
        mock_bot.send_message.call_args[0][1]
        == '*Unable to get news summary.*'
    )
    assert mock_bot.send_message.call_args[1]['parse_mode'] == 'Markdown'
