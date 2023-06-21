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
    :rtype: None
    """
    logger.debug('bot_history()')
    user_id, chat_id = message.from_user.id, message.chat.id
    bot.delete_state(user_id, chat_id)
    items = SearchHistory.get_recent(user_id)
    if not items or len(items) == 0:
        bot.send_message(user_id, '*Search history is empty*',
                         parse_mode='Markdown')
    else:
        menu = history_menu.main(items)
        bot.send_message(user_id, '*Search history:*',
                         reply_markup=menu, parse_mode='Markdown')


# TODO: allow only when state is None or state = NewsState.got_news
@bot.callback_query_handler(func=lambda call: call.data.startswith('history_'), state=None)
def bot_history_item(callback_query: CallbackQuery) -> None:
    id = int(callback_query.data[8:])
    logger.debug(f'bot_history_item() called with id: {id}')

    user_id, chat_id = callback_query.from_user.id, callback_query.message.chat.id
    bot.delete_state(user_id, chat_id)

    item = SearchHistory.get_by_id(id)
    if item:
        # text = f'Query: {item.query}\n' \
        #        f'Date range: {item.date_from}-{item.date_to}\n'
        # bot.send_message(user_id, text)

        get_results(chat_id, chat_id, item.query, item.date_from, item.date_to)
    else:
        bot.send_message(user_id, 'Item not found')
