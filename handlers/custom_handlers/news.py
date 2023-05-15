import requests
from loguru import logger
from telebot.handler_backends import State
from telebot.types import Message

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
    bot.reset_data(message.from_user.id, message.chat.id)

    bot.set_state(message.from_user.id,
                  NewsState.search_query, message.chat.id)
    bot.send_message(message.chat.id, 'Enter search query:')


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
        _handle_valid(message, save_key='search_query', save_value=search_query,
                      next_state=NewsState.date_from,
                      next_message='Enter start date in format 2000-01-01:')
    else:
        _handle_invalid(message, 'Search query cannot be empty.')


@bot.message_handler(state=NewsState.date_from)
def date_from(message: Message) -> None:
    """
    Handles start date

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    date = message.text
    if news_utils.is_date_valid(date):
        _handle_valid(message, save_key='date_from', save_value=date,
                      next_state=NewsState.date_to,
                      next_message='Enter end date in format 2000-01-01:')
    else:
        _handle_invalid(message, 'Invalid date format.')


@bot.message_handler(state=NewsState.date_to)
def date_to(message: Message) -> None:
    """
    Handles end date

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    date = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        date_from_ = data['date_from']

    if not news_utils.is_date_valid(date):
        _handle_invalid(message, 'Invalid date format.')
    elif date < date_from_:
        _handle_invalid(message, 'End date cannot be less than start date.')
    else:
        _handle_valid(message, save_key='date_to', save_value=date,
                      next_state=NewsState.getting_news,
                      next_message='Getting news...')

        _get_news(message.chat.id, message.from_user.id)


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


def _handle_valid(message: Message, save_key: str, save_value: str,
                  next_state: State, next_message: str) -> None:
    """
    Handles valid input: stores a key and sets next state

    :param message: incoming message
    :type message: Message
    :param save_key: key to store in data
    :type save_key: str
    :param save_value: value to store in data
    :type save_value: str
    :param next_state: next state
    :type next_state: State
    :param input_message: message to send to user
    :type input_message: str
    :rtype: None
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data[save_key] = save_value
        data['invalid_count'] = 0

    bot.set_state(message.from_user.id, next_state, message.chat.id)
    bot.send_message(message.chat.id, next_message)


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
