import os
from datetime import date, datetime, timedelta
from unittest.mock import patch

from tests.test_utils import load_news_from_dir

with patch('database.init_db.init_db'), patch(
    'database.init_db.create_tables'
):
    from utils.news import news_api
    from utils.news.utils import date_from_to_str, date_to_to_str


def mock_news_page(news, page_num, page_size):
    i_start = (page_num - 1) * page_size
    i_end = page_num * page_size
    news_part = news[i_start:i_end]
    page = {'totalResults': len(news), 'articles': news_part}
    return page


def get_news_test_data(n_pages: int) -> tuple[list[dict], int]:
    """
    Gets news from json files

    :param n_pages: number of files (pages) to load from
    :type n_pages: int
    :return: news
    :rtype: tuple[list[dict], int]
    """
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    news = load_news_from_dir(data_dir)
    page_size = len(news) // n_pages
    return news, page_size


@patch('utils.news.news_api.PAGE_SIZE', 10)
@patch('utils.news.news_api._get_news_page')
def test_get_news(mock_get_news_page):
    news, page_size = get_news_test_data(3)
    mock_get_news_page.side_effect = (
        lambda q, page_number, s, f, t: mock_news_page(
            news, page_number, page_size
        )
    )
    actual, news_total = news_api.get_news(
        'Ecology', date(2020, 1, 1), date(2020, 1, 3)
    )
    assert news_total == len(news)
    assert actual == news[:page_size]


@patch('utils.news.news_api._get_news_page')
def test_add_first_page_of_news(mock_get_news_page):
    news_test_data, page_size = get_news_test_data(3)
    mock_get_news_page.side_effect = (
        lambda q, page_number, s, f, t: mock_news_page(
            news_test_data, page_number, page_size
        )
    )

    news = []
    n_news_total, query_time = news_api.add_first_page_of_news(
        news, 'Ecology', date(2020, 1, 1), date(2020, 1, 3), 10
    )

    assert n_news_total == len(news_test_data)
    assert query_time >= news_api.MIN_REQUEST_INTERVAL
    assert len(news) == 10
    assert news == news_test_data[:10]


def test__get_queries_count():
    """
    Tests get_planned_queries_count
    """
    assert 10 == news_api._get_queries_count(0.1, 100, 1, 100)
    assert 5 == news_api._get_queries_count(0.1, 100, 1, 5)
    assert 1 == news_api._get_queries_count(0.1, 100, 1, 1)
    assert 0 == news_api._get_queries_count(0.1, 100, 1, -1)
    assert 1 == news_api._get_queries_count(1, 100, 1, 7)
    assert 0 == news_api._get_queries_count(10.2, 5, 1, 100)


def test__get_random_page_numbers():
    actual = news_api._get_random_page_numbers(0, 10, 10)
    assert actual == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    actual = news_api._get_random_page_numbers(0, 10, 1)
    assert len(actual) == 1 and 1 <= actual[0] <= 10

    actual = news_api._get_random_page_numbers(0, 10, 2)
    assert len(actual) == 2 and 1 <= actual[0] <= 5 and 6 <= actual[1] <= 10

    actual = news_api._get_random_page_numbers(0, 10, 3)
    assert (
        len(actual) == 3
        and 1 <= actual[0] <= 3
        and 4 <= actual[1] <= 7
        and 8 <= actual[2] <= 10
    )


@patch('utils.news.news_api._get_news_page')
@patch('utils.news.news_api.get_json_value')
def test_add_news(mock_get_json_value, mock_get_news_page):
    news = []
    search_query = 'test'
    date_from = date(2023, 1, 1)
    date_to = date(2023, 12, 31)
    page_numbers = [1, 2, 3]
    news_per_page = 10
    mock_page = {'articles': [{'id': 1}, {'id': 2}], 'totalResults': '2'}
    mock_get_news_page.return_value = mock_page
    mock_get_json_value.side_effect = lambda json_obj, keys: json_obj[keys[0]]

    result = news_api._add_news(
        news, search_query, date_from, date_to, page_numbers, news_per_page
    )

    assert len(news) == 6
    assert result == 6
    mock_get_news_page.n_calls == 3
    mock_get_news_page.assert_called_with(
        search_query, page_numbers[-1], news_per_page, date_from, date_to
    )
    mock_get_json_value.assert_called_with(mock_page, ['totalResults'])


@patch('utils.news.news_api.config.NEWS_API_KEY', new='1234567890')
@patch('utils.news.news_api.config.NEWS_ID', new='id')
@patch('uuid.uuid4')
def test__get_news_page(uuid4_mock, requests_mock):
    uuid4_mock.return_value.hex = '1234567890'

    url = 'https://newsapi.org/v2/everything'
    method = 'GET'
    search_query = 'test'
    page_number = 1
    page_size = 10
    date_from = date(2020, 1, 1)
    date_to = date(2020, 1, 2)

    request = {
        'apiKey': '1234567890',
        'q': search_query,
        'language': 'en',
        'from': date_from_to_str(date_from, True),
        'to': date_to_to_str(date_to, True),
        'sort': 'relevancy',
        'page': page_number,
        'pageSize': page_size,
    }

    expected_response = {
        'status': 'ok',
        'totalResults': 1,
        'articles': [
            {
                'id': '1234567890',
                'title': 'test',
                'description': 'test',
                'url': 'https://test.com',
                'datePublished': '2020-01-01T00:00:00.000Z',
                'content': 'test',
            }
        ],
    }

    requests_mock.register_uri(
        method, url, json=expected_response, status_code=200
    )

    start_time = datetime.utcnow()
    response = news_api._get_news_page(
        search_query, page_number, page_size, date_from, date_to
    )
    end_time = datetime.utcnow()

    assert response == expected_response
    assert end_time - start_time >= timedelta(seconds=1)
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.method == method
    assert requests_mock.last_request.url.startswith(url)
    assert set(map(str.lower, request.keys())).issubset(
        set(requests_mock.last_request.qs.keys())
    )
    assert requests_mock.last_request.timeout == 60
