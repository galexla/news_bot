from unittest.mock import patch

import pytest
from telebot.types import Chat, Message, User

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from handlers.default_handlers import start


@pytest.fixture
def message():
    user = User(1, False, first_name='test_user')
    message = Message(1, user, 0, Chat(1, 'private'), '', {}, '{}')
    message.text = '/start'
    return message


@patch('handlers.default_handlers.start.bot')
def test_bot_click_news_item_error(mock_bot, message):
    start.bot_start(message)

    mock_bot.delete_state.assert_called_once_with(
        message.from_user.id, message.chat.id)

    mock_bot.reply_to.assert_called_once_with(
        message, f'Hello, {message.from_user.full_name}!')
