import re

import requests
from loguru import logger
from telebot.types import CallbackQuery
from textblob import TextBlob

from loader import bot
from states.news_state import NewsState
from utils.emotions import get_emotions
from utils.misc import get_text_excerpts, redis_cache
from utils.news import utils as news_utils
from utils.news.important_words import get_important_words, get_words


@bot.callback_query_handler(func=lambda call: call.data.startswith('emotions_'), state=NewsState.got_news)
def bot_noun_phrases(call: CallbackQuery):
    """
    Gets noun phrases from a news article

    :param call: callback query
    :type call: CallbackQuery
    :rtype: None
    """
    logger.debug('bot_noun_phrases() called')

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    news_id = re.search(r'^emotions_(\d+)$', call.data).group(1).strip()

    search_query, datetime_from, datetime_to, _, _ = \
        news_utils.retrieve_user_input(chat_id, user_id)

    key = redis_cache.get_key('most_important_news', search_query,
                              datetime_from, datetime_to)
    most_important_news = redis_cache.get(key)
    if not most_important_news:
        raise ValueError('Most important news not found.')

    news_item = most_important_news[news_id]['news']
    text_keys = ['title', 'description', 'body']
    text = '\n\n'.join(news_item.get(key, '') for key in text_keys)
    # text = get_text_excerpts(text, 6000)

    important_words = get_important_words(text)
    noun_phrases = get_noun_phrases(text)
    noun_phrases_importance = get_noun_phrases_importance(
        noun_phrases, important_words)
    # noun_phrases = '\n'.join(noun_phrases[:10])
    noun_phrases = '\n'.join(
        (phrase for phrase, _ in noun_phrases_importance[:10]))

    if noun_phrases:
        title = news_item['title']
        message_text = f'Noun phrases in the news article "{title}":\n{noun_phrases}'
        bot.send_message(chat_id, message_text)
    else:
        bot.send_message(chat_id, 'Unable to get noun phrases.')


def get_noun_phrases(text: str) -> list[str]:
    """
    Gets noun phrases from text

    :param text: text
    :type text: str
    :return: noun phrases
    :rtype: list[str]
    """
    blob = TextBlob(text)
    return blob.noun_phrases


def get_noun_phrases_importance(noun_phrases: list[str],
                                important_words: dict[str, float]) -> list[tuple[str, float]]:
    """
    Gets noun phrases and importance sorted by importance

    :param noun_phrases: noun phrases
    :type noun_phrases: list[str]
    :param important_words: important words
    :type important_words: dict[str, float]
    :return: noun phrases and importance sorted by importance
    :rtype: list[tuple[str, float]]
    """
    noun_phrases_importance = {}

    for noun_phrase in noun_phrases:
        words = get_words(noun_phrase)
        importance = 0
        for word in words:
            if word in important_words:
                importance += important_words[word]
        noun_phrases_importance[noun_phrase] = importance

    noun_phrases_importance = sorted(noun_phrases_importance.items(),
                                     key=lambda item: item[1], reverse=True)
    return noun_phrases_importance


def bot_emotions(call: CallbackQuery):
    """
    Gets emotions from a news article using GPT-3 chatbot

    :param call: callback query
    :type call: CallbackQuery
    :rtype: None
    """
    logger.debug('bot_emotions() called')

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    news_id = re.search(r'^emotions_(\d+)$', call.data).group(1).strip()

    search_query, datetime_from, datetime_to, _, _ = \
        news_utils.retrieve_user_input(chat_id, user_id)

    try:
        key = redis_cache.get_key('most_important_news', search_query,
                                  datetime_from, datetime_to)
        most_important_news = redis_cache.get(key)
        if not most_important_news:
            raise KeyError('Most important news not found.')

        news_item = most_important_news[news_id]['news']
        text = news_item['body']
        text = get_text_excerpts(text, 2000)

        key_emotions = redis_cache.get_key('emotions', news_id)
        cached_get_emotions = redis_cache.cached(
            key_emotions, datetime_to)(get_emotions)
        emotions = cached_get_emotions(text)

        if emotions:
            title = news_item['title']
            message_text = f'Emotions in the news article "{title}":\n{emotions}'
            bot.send_message(chat_id, message_text)
        else:
            bot.send_message(chat_id, 'Unable to get emotions.')
    except (requests.RequestException, ValueError,
            requests.exceptions.JSONDecodeError) as exception:
        logger.exception(exception)
        bot.send_message(chat_id, 'Some error occurred.')
