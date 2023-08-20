from unittest.mock import patch

import pytest
from telebot.types import Chat, Message, User

with patch('database.init_db.init_db'), patch(
    'database.init_db.create_tables'
):
    from handlers.default_handlers import echo


@pytest.fixture
def message():
    user = User(1, False, first_name='test_user')
    message = Message(1, user, 0, Chat(1, 'private'), '', {}, '{}')
    message.text = '/echo'
    return message


@patch('handlers.default_handlers.echo.bot')
def test_bot_click_news_item_error(mock_bot, message):
    echo.bot_echo(message)

    mock_bot.reply_to.assert_called_once()
    assert mock_bot.reply_to.call_args[0][0] == message
    assert mock_bot.reply_to.call_args[0][1].startswith('Your message: ')
