from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from utils.misc.api_query_scheduler import ApiQuery, ApiQueryScheduler


def test_ApiQuery():
    with pytest.raises(ValueError):
        ApiQuery('test', 'url', {'a': 'b'}, {'c': 'd'}, 1, 2)

    query = ApiQuery('GET', 'url', {'a': 'b'}, {'c': 'd'}, 1, 2)
    assert query._method == 'GET'
    assert query._url == 'url'
    assert query._headers == {'a': 'b'}
    assert query._body == {'c': 'd'}
    assert query._interval == 1
    assert query._timeout == 2
    assert query._start_time is None
    assert query._end_time is None
    assert query.interval == 1
    assert query.start_time is None
    assert query.end_time is None

    query = ApiQuery('post', 'url', {'a': 'b'}, {'c': 'd'}, 1, 2)
    query.start_time = 'a'
    assert query.start_time == 'a'
    query.end_time = 'b'
    assert query.end_time == 'b'


@pytest.mark.parametrize('method, url, headers, body, interval, timeout, status_code, expected_response', [
    ('GET', 'http://test.com', {'content-type': 'application/json'},
     {'key': 'value'}, 5, 10, 200, {'result': 'success'}),
    ('POST', 'http://test.com', {'content-type': 'application/json'},
     {'key': 'value'}, 5, 10, 200, {'result': 'success'}),
    ('POST', 'http://test.com',
     {'content-type': 'application/json'}, {'key': 'value'}, 5, 10, 201, None),
    ('GET', 'http://test.com',
     {'content-type': 'application/json'}, {'key': 'value'}, 5, 10, 400, None),
    ('POST', 'http://test.com',
     {'content-type': 'application/json'}, {'key': 'value'}, 5, 10, 500, None),
])
def test_ApiQuery_execute(method, url, headers, body, interval, timeout, status_code, expected_response, requests_mock):
    api_query = ApiQuery(method, url, headers, body, interval, timeout)
    requests_mock.register_uri(
        api_query._method, api_query._url, json=expected_response, status_code=status_code)

    response = api_query.execute()

    if expected_response is None:
        assert response is None
    else:
        assert response == expected_response
    assert requests_mock.last_request.method == api_query._method
    assert requests_mock.last_request.timeout == api_query._timeout


@pytest.mark.parametrize('interval, from_start, time_delta, expected_result', [
    (1,   True,  1.2, 0),
    (1,   True,  0.8, 0.2),
    (1.5, True,  1.2, 0.3),
    (1.5, False, 1.2, 0.3),
])
def test_ApiQueryScheduler_get_sleep_time(interval, from_start, time_delta, expected_result):
    query = ApiQuery('GET', 'url', {'a': 'b'}, {'c': 'd'}, interval, 2)
    ApiQueryScheduler.from_start = from_start
    if from_start:
        query.start_time = datetime.utcnow() - timedelta(seconds=time_delta)
    else:
        query.end_time = datetime.utcnow() - timedelta(seconds=time_delta)
    actual = ApiQueryScheduler._ApiQueryScheduler__get_sleep_time(query)
    assert round(actual, 4) == expected_result


def test_ApiQueryScheduler_get_sleep_time_none():
    assert ApiQueryScheduler._ApiQueryScheduler__get_sleep_time(None) == 0


def test_ApiQueryScheduler_get_sleep_time_no_start_end():
    query = ApiQuery('GET', 'url', {'a': 'b'}, {'c': 'd'}, 1, 2)
    assert ApiQueryScheduler._ApiQueryScheduler__get_sleep_time(query) == 0


@pytest.mark.parametrize('interval, expected_result', [
    (0.2, 0.2),
    (0.5, 0.5),
    (0.7, 0.7),
])
def test_ApiQueryScheduler_execute(interval, expected_result, requests_mock):
    query = ApiQuery('GET', 'http://test.com', {'content-type': 'application/json'},
                     {'key': 'value'}, interval, 10)
    requests_mock.register_uri(
        query._method, query._url, json={'result': 'success'}, status_code=200)

    start_time = datetime.utcnow()
    ApiQueryScheduler.execute(query)
    end_time = datetime.utcnow()

    assert end_time - start_time >= timedelta(seconds=expected_result)
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.method == query._method
    assert requests_mock.last_request.timeout == query._timeout


def test_ApiQueryScheduler_execute_series(requests_mock):
    query1 = ApiQuery('GET', 'http://test.com', {'content-type': 'application/json'},
                      {'key': 'value'}, 0.5, 10)
    query2 = ApiQuery('GET', 'http://test.com', {'content-type': 'application/json'},
                      {'key': 'value'}, 0.2, 10)
    requests_mock.register_uri(
        query1._method, query1._url, json={'result': 'success'}, status_code=200)

    start_time1 = datetime.utcnow()
    ApiQueryScheduler.execute(query1)
    end_time1 = datetime.utcnow()

    start_time2 = datetime.utcnow()
    ApiQueryScheduler.execute(query2)
    end_time2 = datetime.utcnow()

    assert end_time2 - start_time1 >= timedelta(seconds=0.7)
    assert requests_mock.call_count == 2
