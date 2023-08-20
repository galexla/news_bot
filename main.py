from telebot.custom_filters import StateFilter

import debugger  # noqa
import handlers  # noqa
from config_data import config  # noqa
from loader import bot
from utils.set_bot_commands import set_default_commands

bot.add_custom_filter(StateFilter(bot))
set_default_commands(bot)
bot.polling(non_stop=True, interval=1)
