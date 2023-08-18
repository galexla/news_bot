from datetime import datetime

from loguru import logger
from telebot.types import CallbackQuery, Message

from database.models.SearchHistory import SearchHistory
from handlers.custom_handlers.news_results import get_results
from keyboards.reply import history_menu
from loader import bot


@bot.message_handler(commands=['history'])
def bot_history(message: Message) -> None:
    """
    Handles the /history command

    :param message: incoming message
    :type message: Message
    :return: None
    """
    logger.debug('bot_history()')

    user_id, chat_id = message.from_user.id, message.chat.id
    bot.delete_state(user_id, chat_id)

    items = SearchHistory.get_recent(user_id)
    if not items or len(items) == 0:
        bot.send_message(chat_id, '*Search history is empty*',
                         parse_mode='Markdown')
    else:
        menu = history_menu.main(items)
        bot.send_message(chat_id, '*Search history:*',
                         reply_markup=menu, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith('history_'), state=None)
def bot_history_item(call: CallbackQuery) -> None:
    """
    Handles the history_* callback query

    :param call: incoming callback query
    :type call: CallbackQuery
    :return: None
    """
    logger.debug('bot_history_item()')

    id = int(call.data[8:])
    logger.debug(f'bot_history_item() called with id: {id}')

    chat_id, user_id = call.message.chat.id, call.from_user.id
    bot.delete_state(user_id, chat_id)

    item = SearchHistory.get_by_id(id)
    if item:
        item.entered_date = datetime.now()
        item.save()
        get_results(chat_id, user_id, item.query, item.date_from, item.date_to)
    else:
        bot.send_message(chat_id, 'Item not found')
