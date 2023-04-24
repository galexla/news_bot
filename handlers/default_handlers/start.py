from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    """
    Starts the bot

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    bot.reply_to(message, f'Привет, {message.from_user.full_name}!')
