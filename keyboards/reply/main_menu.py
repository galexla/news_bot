from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def menu() -> InlineKeyboardMarkup:
    menu_ = InlineKeyboardMarkup()
    menu_.add(InlineKeyboardButton(text='Get summary', callback_data='summary'))
    menu_.add(InlineKeyboardButton(text='Get 5 most important news', callback_data='top_news'))

    return menu_
