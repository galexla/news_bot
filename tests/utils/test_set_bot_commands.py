from unittest.mock import Mock, call, patch

import pytest
from telebot import TeleBot
from telebot.types import BotCommand

with patch('database.init_db.init_db'), patch(
    'database.init_db.create_tables'
):
    from utils.set_bot_commands import set_default_commands

DEFAULT_COMMANDS = [('command1', 'description1'), ('command2', 'description2')]


@pytest.fixture
def mock_bot():
    return Mock(spec=TeleBot)


@pytest.fixture
def mock_bot_command():
    return Mock(spec=BotCommand)


def test_set_default_commands(mock_bot, mock_bot_command):
    with patch('utils.set_bot_commands.BotCommand', new=mock_bot_command):
        with patch(
            'utils.set_bot_commands.DEFAULT_COMMANDS', new=DEFAULT_COMMANDS
        ):
            set_default_commands(mock_bot)
            calls = [call(*i) for i in DEFAULT_COMMANDS]
            mock_bot_command.assert_has_calls(calls, any_order=True)
            mock_bot.set_my_commands.assert_called_once_with(
                [mock_bot_command(*i) for i in DEFAULT_COMMANDS]
            )
