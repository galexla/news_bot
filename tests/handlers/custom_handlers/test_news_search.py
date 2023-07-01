from unittest.mock import MagicMock, patch

import pytest

from states.news_state import NewsState

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from handlers.custom_handlers import news_search


@pytest.fixture
def message():
    msg = MagicMock()
    msg.chat.id = 1234
    msg.from_user.id = 5678
    msg.text = "News Query"
    return msg


@pytest.fixture
def lstep_mock():
    return [1, 2, 3]


@pytest.fixture
def mock_manager():
    def _create_mock_manager(n_invalid_inputs):
        data = {'n_invalid_inputs': n_invalid_inputs}
        mock_manager = MagicMock()
        mock_manager.__enter__.return_value = data
        mock_manager.__exit__.return_value = None
        return mock_manager
    return _create_mock_manager


@patch('handlers.custom_handlers.news_search.bot')
def test_bot_news_start(bot_mock, message):
    news_search.bot_news_start(message)
    bot_mock.reset_data.assert_called_once_with(
        message.from_user.id, message.chat.id)
    bot_mock.set_state.assert_called_once_with(
        message.from_user.id, NewsState.enter_search_query, message.chat.id)
    bot_mock.send_message.assert_called_once_with(
        message.chat.id, '*Enter search query:*', parse_mode='Markdown')


@patch('handlers.custom_handlers.news_search.bot')
def test_bot_enter_search_query(bot_mock, message):
    news_search.bot_enter_search_query(message)
    bot_mock.retrieve_data.assert_called_once_with(
        message.from_user.id, message.chat.id)
    bot_mock.set_state.assert_called_once_with(
        message.from_user.id, NewsState.enter_dates, message.chat.id)
    bot_mock.send_message.assert_called_once()


@pytest.mark.parametrize("invalid_inputs", [3, 5, 10])
@patch('handlers.custom_handlers.news_search.bot')
def test__handle_invalid_input(bot_mock, mock_manager, message, invalid_inputs):
    bot_mock.retrieve_data.return_value = mock_manager(invalid_inputs)

    error_message = 'Search query cannot be empty.'
    news_search._handle_invalid_input(message, error_message)
    bot_mock.retrieve_data.assert_called_once_with(
        message.from_user.id, message.chat.id)
    bot_mock.delete_state.assert_called_once_with(
        message.from_user.id, message.chat.id)
    bot_mock.reply_to.assert_called_once()


@pytest.mark.parametrize("invalid_inputs", [0, 1, 2])
@patch('handlers.custom_handlers.news_search.bot')
def test__handle_invalid_input(bot_mock, mock_manager, message, invalid_inputs):
    bot_mock.retrieve_data.return_value = mock_manager(invalid_inputs)

    error_message = 'Search query cannot be empty.'
    news_search._handle_invalid_input(message, error_message)
    bot_mock.retrieve_data.assert_called_once_with(
        message.from_user.id, message.chat.id)
    bot_mock.delete_state.assert_not_called()
    bot_mock.reply_to.assert_called_once()


@patch('handlers.custom_handlers.news_search.LSTEP')
@patch('handlers.custom_handlers.news_search.bot')
@patch('handlers.custom_handlers.news_search.DetailedTelegramCalendar')
def test__display_calendar(calendar_mock, bot_mock, lstep_mock):
    user_id = 123
    calendar_mock().build.return_value = (MagicMock(), 0)
    news_search._display_calendar(user_id)
    bot_mock.send_message.assert_called_once()
    assert bot_mock.send_message.call_args[0][0] == user_id
    assert bot_mock.send_message.call_args[0][1].startswith(
        '*Select week by pressing on any date.\nSelect')
    assert bot_mock.send_message.call_args[0][1].endswith('*')
    assert bot_mock.send_message.call_args[1]['parse_mode'] == 'Markdown'
    assert bot_mock.send_message.call_args[1]['reply_markup'] == calendar_mock(
    ).build.return_value[0]
