from loader import bot
import handlers  # noqa
from utils.set_bot_commands import set_default_commands

import debugpy

if __name__ == '__main__':
    # TODO: remove
    debugpy.listen(('0.0.0.0', 5678))

    set_default_commands(bot)
    bot.polling(non_stop=True, interval=1)
