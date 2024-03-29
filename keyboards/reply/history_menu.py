import textwrap
from datetime import datetime
from typing import Iterable

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.models.SearchHistory import SearchHistory


def main(history: Iterable[SearchHistory]) -> InlineKeyboardMarkup:
    """
    Menu that displays search history. Each menu item is a button with search
    query and dates in title. It keeps callback data in format 'history_{id}'.

    :param history: list of SearchHistory objects
    :type history: Iterable[SearchHistory]
    :return: menu
    :rtype: InlineKeyboardMarkup
    """
    menu = InlineKeyboardMarkup()
    for item in history:
        date_from = datetime.strftime(item.date_from, '%d.%m.%y')
        date_to = datetime.strftime(item.date_to, '%d.%m.%y')
        text = f'{date_from} - {date_to} {item.query}'
        text = textwrap.fill(text)

        data = f'history_{item.id}'

        menu.add(InlineKeyboardButton(text=text, callback_data=data))

    return menu
