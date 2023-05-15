from typing import Iterable

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def main(news: Iterable[dict]) -> InlineKeyboardMarkup:
    menu_ = InlineKeyboardMarkup()
    for item in news:
        text = item['title'][:50] + '...'
        data = f'news_{item["id"]}'
        menu_.add(InlineKeyboardButton(text=text, callback_data=data))

    return menu_


def submenu(news_id: str, url: str) -> InlineKeyboardMarkup:
    menu_ = InlineKeyboardMarkup()
    data = f'emotions_{news_id}'
    menu_.add(InlineKeyboardButton(text='Get emotions', callback_data=data))
    menu_.add(InlineKeyboardButton(text='Read article', url=url))

    return menu_
