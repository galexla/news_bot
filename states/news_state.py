from telebot.handler_backends import State, StatesGroup


class NewsState(StatesGroup):
    """
    States for /news command
    """
    enter_search_query = State()
    enter_dates = State()
    getting_news = State()
    got_news = State()
