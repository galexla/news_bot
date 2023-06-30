from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from telebot.types import CallbackQuery, Chat, Message, User

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from handlers.custom_handlers import history


@pytest.fixture
def message():
    user = User(1, False, first_name='test_user')
    message = Message(1, user, 0, Chat(1, 'private'), '', {}, '{}')
    message.text = '/history'
    return message


@pytest.fixture
def callback_query():
    user = User(1, False, first_name='test_user')
    message = Message(1, user, 0, Chat(1, 'private'), '', {}, '{}')
    query = CallbackQuery('1', user, data='history_1', chat_instance='private',
                          json_string='{}', message=message)
    return query


@pytest.fixture
def recent_history():
    result = []
    for i in range(1, 3):
        obj = MagicMock()
        obj.query = 'query'
        obj.date_from = date(2022, 1, 1)
        obj.date_to = date(2022, 1, 2)
        result.append(obj)
    return result


@patch('handlers.custom_handlers.history.bot')
@patch('handlers.custom_handlers.news_results.bot')
@patch('handlers.custom_handlers.history.SearchHistory')
def test_bot_history(mock_history, mock_bot_news_results,
                     mock_bot_history, recent_history, message):
    mock_history.get_recent.return_value = recent_history

    history.bot_history(message)

    mock_bot_history.delete_state.assert_called_once_with(
        message.from_user.id, message.chat.id)
    mock_history.get_recent.assert_called_once_with(message.from_user.id)
    mock_bot_history.send_message.assert_called_once()
    assert mock_bot_history.send_message.call_args[0][0] == message.chat.id
    assert mock_bot_history.send_message.call_args[0][1] == '*Search history:*'
    assert mock_bot_history.send_message.call_args[1]['parse_mode'] == 'Markdown'
    assert mock_bot_history.send_message.call_args[1]['reply_markup'] is not None


@patch('handlers.custom_handlers.history.bot')
@patch('handlers.custom_handlers.news_results.bot')
@patch('handlers.custom_handlers.history.SearchHistory')
@patch('handlers.custom_handlers.history.get_results')
def test_bot_history_item(mock_get_results, mock_history, mock_bot_news_results,
                          mock_bot_history, recent_history, callback_query):
    history_item = recent_history[0]
    mock_history.get_by_id.return_value = history_item

    history.bot_history_item(callback_query)

    mock_bot_history.delete_state.assert_called_once_with(
        callback_query.from_user.id, callback_query.message.chat.id)
    mock_history.get_by_id.assert_called_once_with(
        int(callback_query.data[8:]))
    mock_get_results.assert_called_once_with(
        callback_query.from_user.id, callback_query.message.chat.id,
        history_item.query, history_item.date_from, history_item.date_to)


@patch('handlers.custom_handlers.history.bot')
@patch('handlers.custom_handlers.news_results.bot')
@patch('handlers.custom_handlers.history.SearchHistory')
@patch('handlers.custom_handlers.history.get_results')
def test_bot_history_item(mock_get_results, mock_history, mock_bot_news_results,
                          mock_bot_history, recent_history, callback_query):
    mock_history.get_by_id.return_value = False

    history.bot_history_item(callback_query)

    mock_bot_history.delete_state.assert_called_once_with(
        callback_query.from_user.id, callback_query.message.chat.id)
    mock_history.get_by_id.assert_called_once_with(
        int(callback_query.data[8:]))
    mock_get_results.assert_not_called()
    mock_bot_history.send_message.assert_called_with(
        callback_query.message.chat.id, 'Item not found')
