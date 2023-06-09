import requests
from loguru import logger
from telebot.types import CallbackQuery, Message
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar

from keyboards.reply import news_menu
from loader import bot
from states.news_state import NewsState
from utils.misc import redis_cache as cache
from utils.news import utils as news_utils
from utils.news.news import get_news_semimanufactures
from utils.summary import get_summary
from utils.top_news import get_top_news


@bot.message_handler(commands=['news'])
def bot_news_start(message: Message) -> None:
    """
    Handles the /news command

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    bot.reset_data(message.from_user.id)

    bot.set_state(message.from_user.id, NewsState.enter_search_query)
    bot.send_message(message.from_user.id, 'Enter search query:')


@bot.message_handler(state=NewsState.enter_search_query)
def bot_enter_search_query(message: Message) -> None:
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

        bot.set_state(message.from_user.id, NewsState.enter_dates)
        _display_calendar(message.from_user.id)
    else:
        _handle_invalid_input(message, 'Search query cannot be empty.')


def _display_calendar(user_id: int) -> None:
    """
    Displays calendar

    :rtype: None
    """
    calendar, step = DetailedTelegramCalendar().build()
    text_msg = 'Select week (by pressing on any date in the week).'
    bot.send_message(
        user_id, f'{text_msg}\nSelect {LSTEP[step]}', reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def bot_work_with_calendar(callback_query: CallbackQuery) -> None:
    """Handles work with visual calendar"""
    text_msg = 'Select week (by pressing on any date in the week).'
    message = callback_query.message
    result, key, step = DetailedTelegramCalendar().process(callback_query.data)
    if not result and key:
        bot.edit_message_text(f"{text_msg}\nSelect {LSTEP[step]}",
                              message.chat.id,
                              message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              message.chat.id,
                              message.message_id)

        with bot.retrieve_data(message.chat.id, message.chat.id) as data:
            first_day = news_utils.get_first_day_of_week(result)
            last_day = news_utils.get_last_day_of_week(result)
            data['date_from'] = first_day.strftime('%Y-%m-%d')
            data['date_to'] = last_day.strftime('%Y-%m-%d')

        bot.set_state(message.chat.id, NewsState.getting_news)
        bot.send_message(
            message.chat.id, 'Getting news... It can take up to 6 seconds.')

        _get_results(message.chat.id, message.chat.id)


def _get_results(chat_id: int, user_id: int) -> None:
    """
    Gets and displays news count, summary and top news

    :param chat_id: chat id
    :type chat_id: int
    :param user_id: user id
    :type user_id: int
    :rtype: None
    """
    try:
        search_query, datetime_from, datetime_to, date_from, date_to = \
            news_utils.retrieve_query_info(user_id, chat_id)
        news_count, summary_input, important_news = get_news_semimanufactures(
            search_query, datetime_from, datetime_to)

        text_msg = f'Got {news_count} news for a search query "{search_query}" '\
            f'from {date_from} to {date_to}.\nGenerating summary and top news,'\
            'please wait...'
        bot.send_message(chat_id, text_msg)

        summary, top_news = _get_summary_and_top_news(
            search_query, datetime_from, datetime_to,
            summary_input, important_news)

        if summary and top_news:
            bot.set_state(user_id, NewsState.got_news, chat_id)
            _display_summary_and_top_news(chat_id, summary, top_news)
        else:
            bot.delete_state(user_id, chat_id)
            logger.error(
                f'Unable to get summary & top news for query: '
                f'"{search_query}", dates: {datetime_from} - {datetime_to}.')
            bot.send_message(chat_id, 'Unable to get top news.')
    except (requests.RequestException, requests.exceptions.JSONDecodeError,
            ValueError) as exception:
        bot.delete_state(user_id, chat_id)
        logger.exception(exception)
        if isinstance(exception, ValueError):
            bot.send_message(chat_id, 'Error. Invalid data.')
        else:
            bot.send_message(chat_id, 'Some error occurred.')


def _get_summary_and_top_news(search_query: str, datetime_from: str, datetime_to: str,
                              summary_input: str, important_news: dict) -> tuple[list, list]:
    """Gets summary and top news and saves in cache if needed"""
    summary = cache.get_set(cache.key('summary', search_query,
                            datetime_from, datetime_to),
                            cache.get_ttl(datetime_to),
                            get_summary, summary_input)

    top_news = cache.get_set(cache.key('top_news', search_query,
                                       datetime_from, datetime_to),
                             cache.get_ttl(datetime_to),
                             get_top_news, summary, important_news)

    return summary, top_news


def _display_summary_and_top_news(chat_id: str, summary: list[str],
                                  top_news: list[dict]) -> None:
    """Displays summary and top news"""
    text_msg = 'Here is summary of news for the chosen period.\n'
    bot.send_message(chat_id, text_msg + ' '.join(summary))

    text_msg = 'Here are top news. You can choose one to get '
    'its summary or to read the full article.'
    bot.send_message(
        chat_id, text_msg, reply_markup=news_menu.main(top_news))


def _handle_invalid_input(message: Message, error_message: str) -> None:
    """
    Handles invalid input

    :param message: incoming message
    :type message: Message
    :param error_message: error message
    :type error_message: str
    :rtype: None
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data.get('invalid_count', 0) >= 2:
            # if invalid input was entered 3 times, start over
            bot.delete_state(message.from_user.id, message.chat.id)
            text = 'You entered invalid data 3 times. You can start over by entering /news'
            bot.reply_to(message, text)
        else:
            data['invalid_count'] += 1
            bot.reply_to(message, error_message)
