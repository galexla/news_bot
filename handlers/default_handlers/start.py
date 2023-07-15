from loguru import logger
from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Starts the bot

    :param message: incoming message
    :type message: Message
    :return: None
    """
    logger.debug('bot_start()')

    user_id, chat_id = message.from_user.id, message.chat.id
    bot.delete_state(user_id, chat_id)
    bot.reply_to(message, f'Hello, {message.from_user.full_name}!')
