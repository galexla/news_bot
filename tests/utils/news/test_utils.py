from datetime import date

from utils.news import utils as news_utils


def test_get_first_day_of_week() -> None:
    """
    Tests get_first_day_of_week
    """
    date1 = date(2020, 1, 1)
    assert news_utils.get_first_day_of_week(date1) == date(2019, 12, 30)

    date1 = date(2020, 1, 5)
    assert news_utils.get_first_day_of_week(date1) == date(2019, 12, 30)

    date1 = date(2020, 1, 6)
    assert news_utils.get_first_day_of_week(date1) == date(2020, 1, 6)


def test_get_last_day_of_week() -> None:
    """
    Tests get_last_day_of_week
    """
    date1 = date(2019, 12, 27)
    assert news_utils.get_last_day_of_week(date1) == date(2019, 12, 29)

    date1 = date(2019, 12, 30)
    assert news_utils.get_last_day_of_week(date1) == date(2020, 1, 5)

    date1 = date(2020, 1, 6)
    assert news_utils.get_last_day_of_week(date1) == date(2020, 1, 12)
