import re

from loguru import logger
from telebot.types import CallbackQuery, Message
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar

from database.models.SearchHistory import SearchHistory
from handlers.custom_handlers.news_results import get_results
from loader import bot
from states.news_state import NewsState
from utils.news import utils as news_utils

MAX_INVALID_INPUTS = 3


@bot.message_handler(commands=['news'])
def bot_news_start(message: Message) -> None:
    """
    Handles the /news command

    :param message: incoming message
    :type message: Message
    """
    logger.debug('bot_news_start()')

    chat_id, user_id = message.chat.id, message.from_user.id
    bot.set_state(user_id, NewsState.enter_search_query, chat_id)
    bot.reset_data(user_id, chat_id)

    bot.send_message(chat_id, '*Enter search query:*', parse_mode='Markdown')


@bot.message_handler(state=NewsState.enter_search_query)
def bot_enter_search_query(message: Message) -> None:
    """
    Handles search query

    :param message: incoming message
    :type message: Message
    """
    logger.debug('bot_enter_search_query()')

    search_query = message.text.strip()
    chat_id, user_id = message.chat.id, message.from_user.id

    if is_query_valid(search_query):
        with bot.retrieve_data(user_id, chat_id) as data:
            data['n_invalid_inputs'] = 0
            data['search_query'] = search_query

        bot.set_state(user_id, NewsState.enter_dates, chat_id)
        _display_calendar(user_id)
    else:
        _handle_invalid_input(
            message,
            '*Search query must contain letters or numbers an be at'
            'least 3 characters long.\nEnter search query:*',
        )


def is_query_valid(search_query: str) -> bool:
    """
    Checks if search query is valid

    :param search_query: search query
    :type search_query: str
    :return: True if search query is valid, False otherwise
    """
    search_query = search_query.strip(' \t\n\r')
    if not re.search(r'\w', search_query):
        return False

    return len(search_query) >= 3


def _handle_invalid_input(message: Message, error_message: str) -> None:
    """
    Handles invalid input

    :param message: incoming message
    :type message: Message
    :param error_message: error message
    :type error_message: str
    """
    _, user_id = message.chat.id, message.from_user.id
    with bot.retrieve_data(user_id) as data:
        data['n_invalid_inputs'] = data.get('n_invalid_inputs', 0) + 1
        if data['n_invalid_inputs'] >= MAX_INVALID_INPUTS:
            bot.delete_state(user_id)
            text = (
                '*You entered invalid query 3 times. You can start over '
                'by entering /news*'
            )
            bot.reply_to(message, text, parse_mode='Markdown')
        else:
            bot.reply_to(message, error_message, parse_mode='Markdown')


def _display_calendar(user_id: int) -> None:
    """
    Displays calendar

    :param user_id: user id
    :type user_id: int
    """
    calendar, step = DetailedTelegramCalendar().build()
    text_msg = f'*Select week by pressing on any date.\nSelect {LSTEP[step]}*'
    bot.send_message(
        user_id, text_msg, reply_markup=calendar, parse_mode='Markdown'
    )


@bot.callback_query_handler(
    func=DetailedTelegramCalendar.func(), state=NewsState.enter_dates
)
def bot_work_with_calendar(call: CallbackQuery) -> None:
    """
    Handles work with a visual calendar

    :param call: callback query
    :type call: CallbackQuery
    """
    logger.debug('bot_work_with_calendar()')

    message = call.message
    chat_id, user_id = message.chat.id, call.from_user.id
    result, key, step = DetailedTelegramCalendar().process(call.data)
    if not result and key:
        text_msg = (
            f'*Select week by pressing on any date.\nSelect {LSTEP[step]}*'
        )
        bot.edit_message_text(
            text_msg,
            chat_id,
            message.message_id,
            reply_markup=key,
            parse_mode='Markdown',
        )
    elif result:
        # date selected
        first_day = news_utils.get_first_day_of_week(result)
        last_day = news_utils.get_last_day_of_week(result)

        with bot.retrieve_data(user_id, chat_id) as data:
            data['date_from'] = first_day.strftime('%Y-%m-%d')
            data['date_to'] = last_day.strftime('%Y-%m-%d')
            search_query = data['search_query']

        bot.set_state(user_id, NewsState.getting_news, chat_id)

        SearchHistory.add_or_update(
            user_id=chat_id,
            query=search_query,
            date_from=first_day,
            date_to=last_day,
        )

        bot.delete_message(chat_id, message.message_id)
        get_results(chat_id, user_id, search_query, first_day, last_day)
