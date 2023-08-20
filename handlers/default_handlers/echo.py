from loguru import logger
from telebot.types import Message

from loader import bot


@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    """
    Handles all messages that have no other handler and which state is None

    :param message: incoming message
    :type message: Message
    :return: None
    """
    logger.debug('bot_echo()')

    bot.reply_to(
        message, f'Your message: {message.text}'
    )
