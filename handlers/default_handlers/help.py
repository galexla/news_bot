from loguru import logger
from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """
    Handles help message and show a list of commands

    :param message: incoming message
    :type message: Message
    """
    logger.debug('bot_help()')

    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))
