import requests
from loguru import logger
from telebot.types import CallbackQuery, Message
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar

from keyboards.reply import main_menu
from loader import bot
from states.news_state import NewsState
from utils.news import utils as news_utils
from utils.news.news import get_news_semimanufactures


@bot.message_handler(commands=['news'])
def bot_news(message: Message) -> None:
    """
    Handles the /news command

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    bot.reset_data(message.from_user.id)

    bot.set_state(message.from_user.id, NewsState.search_query)
    bot.send_message(message.from_user.id, 'Enter search query:')


@bot.message_handler(state=NewsState.search_query)
def search_query(message: Message) -> None:
    """
    Handles search query

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    search_query = message.text.strip()

    if search_query:
        with bot.retrieve_data(message.from_user.id) as data:
            data['invalid_count'] = 0
            data['search_query'] = search_query

        bot.set_state(message.from_user.id, NewsState.date_from)
        display_calendar(message.from_user.id)
    else:
        _handle_invalid(message, 'Search query cannot be empty.')


def display_calendar(user_id: int) -> None:
    """
    Displays calendar

    :rtype: None
    """
    calendar, step = DetailedTelegramCalendar().build()
    text = 'Select week (by pressing on any date in the week).'
    bot.send_message(
        user_id, f'{text}\nSelect {LSTEP[step]}', reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def calendar(callback_query: CallbackQuery) -> None:
    text = 'Select week (by pressing on any date in the week).'
    message = callback_query.message
    result, key, step = DetailedTelegramCalendar().process(callback_query.data)
    if not result and key:
        bot.edit_message_text(f"{text}\nSelect {LSTEP[step]}",
                              message.chat.id,
                              message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              message.chat.id,
                              message.message_id)

        with bot.retrieve_data(message.chat.id, message.chat.id) as data:
            data['invalid_count'] = 0
            first_day = news_utils.get_first_day_of_week(result)
            last_day = news_utils.get_last_day_of_week(result)
            data['date_from'] = first_day.strftime('%Y-%m-%d')
            data['date_to'] = last_day.strftime('%Y-%m-%d')

        bot.set_state(message.chat.id, NewsState.getting_news)
        bot.send_message(
            message.chat.id, 'Getting news... It can take up to 6 seconds.')

        # TODO: refactor in diff places, keep one argument, also in bot.retrieve_data()
        _get_news(message.chat.id, message.chat.id)


def _get_news(chat_id: int, user_id: int):
    """
    Gets news count, summary input and 50 most important news based
    on news got from API or from cache. Sends a message with news count.

    :param chat_id: chat id
    :type chat_id: int
    :param user_id: user id
    :type user_id: int
    :rtype: None
    """
    try:
        search_query_, datetime_from_, datetime_to_, date_from_, date_to_ = \
            news_utils.retrieve_user_input(user_id, chat_id)
        news_count, _, _ = get_news_semimanufactures(
            search_query_, datetime_from_, datetime_to_)

        bot.set_state(user_id, NewsState.got_news, chat_id)

        text = f'Got {news_count} news for a search query "{search_query_}" '\
            f'from {date_from_} to {date_to_}. Now you can start analyzing them.'
        bot.send_message(chat_id, text, reply_markup=main_menu.menu())
    except (requests.RequestException, requests.exceptions.JSONDecodeError,
            ValueError) as exception:
        logger.exception(exception)
        bot.delete_state(user_id, chat_id)
        if isinstance(exception, ValueError):
            bot.send_message(chat_id, 'Error. Invalid data.')
        else:
            bot.send_message(chat_id, 'Some error occurred.')


def _handle_invalid(message: Message, error_message: str) -> None:
    """
    Handles invalid input

    :param message: incoming message
    :type message: Message
    :param error_message: error message
    :type error_message: str
    :rtype: None
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data.get('invalid_count') >= 2:
            # if invalid input was entered 3 times, delete state
            bot.delete_state(message.from_user.id, message.chat.id)
            text = 'You entered invalid data 3 times. You can start over by entering /news'
            bot.reply_to(message, text)
        else:
            data['invalid_count'] += 1
            bot.reply_to(message, error_message)
