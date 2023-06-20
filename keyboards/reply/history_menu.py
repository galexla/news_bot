import json
import textwrap
from datetime import datetime
from typing import Iterable

# from telebot.callback_data import CallbackData
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.models.SearchHistory import SearchHistory
# from utils.news import utils as news_utils


def main(history: Iterable[SearchHistory]) -> InlineKeyboardMarkup:
    menu = InlineKeyboardMarkup()
    for item in history:
        date_from = datetime.strftime(item.date_from, '%d.%m.%y')
        date_to = datetime.strftime(item.date_to, '%d.%m.%y')
        text = f'{date_from}-{date_to} {item.query}'
        text = textwrap.fill(text)

        # data = CallbackData.new(
        #     action='history_item', search_query=item.query,
        #     date_from=news_utils.date_from_to_str(item.date_from),
        #     date_to=news_utils.date_from_to_str(item.date_to))

        # data = {'action': 'history_item',
        #         'item': {
        #             'search_query': item.query,
        #             'date_from': news_utils.date_from_to_str(item.date_from),
        #             'date_to': news_utils.date_to_to_str(item.date_to)
        #         }}
        # data = json.dumps(data)

        data = f'history_{item.id}'

        menu.add(InlineKeyboardButton(text=text, callback_data=data))

    return menu
