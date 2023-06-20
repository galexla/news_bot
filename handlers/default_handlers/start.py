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
    user_id, chat_id = message.from_user.id, message.chat.id
    bot.delete_state(user_id, chat_id)
    bot.reply_to(message, f'Hello, {message.from_user.full_name}!')
