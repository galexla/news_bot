from datetime import date
import pytest
from utils.news import news_api


def test_get_planned_queries_count():
    """
    Tests get_planned_queries_count
    """
    actual = news_api._get_planned_queries_count(0.1, 100, 1, 100)
    excepted = 10
    assert actual == excepted

    actual = news_api._get_planned_queries_count(0.1, 100, 1, 5)
    excepted = 5
    assert actual == excepted

    actual = news_api._get_planned_queries_count(0.1, 100, 1, 1)
    excepted = 1
    assert actual == excepted

    with pytest.raises(ValueError):
        news_api._get_planned_queries_count(0.1, 100, 1, -1)

    actual = news_api._get_planned_queries_count(1, 100, 1, 7)
    excepted = 1
    assert actual == excepted

    actual = news_api._get_planned_queries_count(10.2, 5, 1, 100)
    excepted = 1
    assert actual == excepted


def test_get_random_page_numbers():
    actual = news_api._get_random_page_numbers(10, 10)
    excepted = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert actual == excepted

    actual = news_api._get_random_page_numbers(10, 1)
    assert len(actual) == 1 and 1 <= actual[0] <= 10

    actual = news_api._get_random_page_numbers(10, 2)
    assert len(actual) == 2 and 1 <= actual[0] <= 5 and 6 <= actual[1] <= 10

    actual = news_api._get_random_page_numbers(10, 3)
    assert len(actual) == 3 and 1 <= actual[0] <= 3 and 4 <= actual[1] <= 7 and 8 <= actual[2] <= 10
