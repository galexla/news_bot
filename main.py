from config_data import config
import debugger

from telebot.custom_filters import StateFilter
import handlers  # noqa
from loader import bot
from utils.set_bot_commands import set_default_commands


bot.add_custom_filter(StateFilter(bot))
set_default_commands(bot)
bot.polling(non_stop=True, interval=1)
