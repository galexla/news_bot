from unittest.mock import patch

import pytest
from telebot.types import Chat, Message, User

from config_data.config import DEFAULT_COMMANDS

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from handlers.default_handlers import help


@pytest.fixture
def message():
    user = User(1, False, first_name='test_user')
    message = Message(1, user, 0, Chat(1, 'private'), '', {}, '{}')
    message.text = '/help'
    return message


@patch('handlers.default_handlers.help.bot')
def test_bot_click_news_item_error(mock_bot, message):
    help.bot_help(message)

    mock_bot.reply_to.assert_called_once_with(
        message, '\n'.join([f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]))
