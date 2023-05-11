from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def menu_markup() -> InlineKeyboardMarkup:
    # menu = ReplyKeyboardMarkup()
    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton(text='Get summary', callback_data='summary'))
    menu.add(InlineKeyboardButton(text='Get top 5 news', callback_data='top5'))
    # menu.add(InlineKeyboardButton(text='List emotions', callback_data='emotions'))

    return menu
