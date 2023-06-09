from typing import Tuple
from telebot.types import CallbackQuery
from utils.news.utils import retrieve_query_info


def retrieve_user_info(call: CallbackQuery) -> Tuple[int, int, str, str, str]:
    """
    Retrieves user info

    :param call: callback query
    :type call: CallbackQuery
    :return: chat id, user id, search query, datetime from, datetime to
    :rtype: Tuple[int, int, str, str, str]
    """
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    search_query, datetime_from, datetime_to, _, _ = \
        retrieve_query_info(chat_id, user_id)
    return chat_id, user_id, search_query, datetime_from, datetime_to
