from typing import Iterable

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def menu(news: Iterable[dict]) -> InlineKeyboardMarkup:
    menu_ = InlineKeyboardMarkup()
    for item in news:
        text = item['title'][:20]
        data = f'emotions_{item["id"]}'
        menu_.add(InlineKeyboardButton(text=text, callback_data=data))

    return menu_
