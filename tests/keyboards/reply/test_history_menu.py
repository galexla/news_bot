from datetime import datetime
from unittest.mock import MagicMock

import pytest
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.models.SearchHistory import SearchHistory
from keyboards.reply import history_menu


@pytest.fixture
def search_history():
    search_history_list = []
    for i in range(1, 3):
        search_history = MagicMock(spec=SearchHistory)
        search_history.date_from = datetime(2022, 1, 1)
        search_history.date_to = datetime(2022, 1, 2)
        search_history.query = f'query{i}'
        search_history.id = i
        search_history_list.append(search_history)
    return search_history_list


def test_main(search_history):
    result = history_menu.main(search_history)

    assert isinstance(result, InlineKeyboardMarkup)
    for i, item in enumerate(search_history, start=1):
        assert isinstance(result.keyboard[i - 1][0], InlineKeyboardButton)
        assert result.keyboard[i -
                               1][0].text == f'01.01.22 - 02.01.22 {item.query}'
        assert result.keyboard[i - 1][0].callback_data == f'history_{i}'
