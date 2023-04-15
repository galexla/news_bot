from dotenv import load_dotenv
import logging
import os
import telebot


if __name__ == '__main__':
    if not load_dotenv():
        raise Exception('No .env file found.')

    bot_token = os.getenv("BOT_TOKEN")

    logger = telebot.logger
    telebot.logger.setLevel(logging.DEBUG)

    bot = telebot.TeleBot(bot_token)


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
    """
    Handles recieved text messages and sends responses

    :type message: telebot.types.Message
    :param message: message received
    :rtype: None
    """
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет и тебе')
    elif message.text == '/hello-world':
        bot.send_message(message.chat.id, 'Привет, мир')


if __name__ == '__main__':
    bot.polling(non_stop=True, interval=1)
