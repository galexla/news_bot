from typing import Iterable

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def main(news: Iterable[dict]) -> InlineKeyboardMarkup:
    menu_ = InlineKeyboardMarkup()
    for item in news:
        id = item['id']
        title = item['title'].strip()
        data = f'news_{id}'
        menu_.add(InlineKeyboardButton(text=title, callback_data=data))

    return menu_


def submenu(news_id: str, url: str) -> InlineKeyboardMarkup:
    menu_ = InlineKeyboardMarkup()
    data = f'emotions_{news_id}'
    menu_.add(InlineKeyboardButton(text='Get emotions', callback_data=data))
    menu_.add(InlineKeyboardButton(text='Read article', url=url))

    return menu_
