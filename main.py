from config_data import config

if __name__ == '__main__':
    if config.DEBUG:
        import debugpy
        debugpy.listen(('0.0.0.0', 5678))
        debugpy.wait_for_client()


from telebot.custom_filters import StateFilter

import handlers  # noqa
from loader import bot
from utils.set_bot_commands import set_default_commands


if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    bot.polling(non_stop=True, interval=1)
