from telebot.types import Message

from loader import bot


@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    """
    Handles all messages that have no other handlers and which state is None

    :param message: incoming message
    :type message: Message
    :rtype: None
    """
    bot.reply_to(
        message, "Echo without state or filter.\n" f"Message: {message.text}"
    )
