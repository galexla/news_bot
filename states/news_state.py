from telebot.handler_backends import State, StatesGroup


class NewsState(StatesGroup):
    """
    States for the /news command
    """
    search_query = State()
    date_from = State()
    date_to = State()
    getting_news = State()
    got_news = State()
