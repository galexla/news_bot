import html
from typing import Iterable

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config_data import config


def main(news: Iterable[dict]) -> InlineKeyboardMarkup:
    """
    Menu that displays news (for example, top news). Each menu item is
    a button with news title. It keeps callback data in format 'news_{news_id}'.

    :param news: list of dicts with keys: id, title
    :type news: Iterable[dict]
    :return: menu
    :rtype: InlineKeyboardMarkup
    """
    menu_ = InlineKeyboardMarkup()
    for item in news:
        id = item[config.NEWS_ID]
        title = item[config.NEWS_TITLE].strip()
        data = f'news_{id}'
        menu_.add(InlineKeyboardButton(text=title, callback_data=data))

    return menu_


def news_item(news_id: str, url: str) -> InlineKeyboardMarkup:
    """
    Menu that displays two buttons for a news item: 'Get summary' and
    'Read article'. It keeps callback data in format 'summary_{news_id}'.

    :param news_id: news id
    :type news_id: str
    :param url: news url
    :type url: str
    :return: menu
    :rtype: InlineKeyboardMarkup
    """
    menu_ = InlineKeyboardMarkup()
    data = f'summary_{news_id}'
    menu_.add(InlineKeyboardButton(text='Get summary', callback_data=data))
    menu_.add(InlineKeyboardButton(text='Read the article', url=url))

    return menu_
