import pytest
import requests_mock

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


@pytest.mark.parametrize("method, url, headers, body, interval, timeout, status_code, expected_response", [
    ('GET', 'http://test.com', {'content-type': 'application/json'}, {'key': 'value'}, 5, 10, 200, {'result': 'success'}),
    ('POST', 'http://test.com', {'content-type': 'application/json'}, {'key': 'value'}, 5, 10, 200, {'result': 'success'}),
    ('POST', 'http://test.com', {'content-type': 'application/json'}, {'key': 'value'}, 5, 10, 201, None),
    ('GET', 'http://test.com', {'content-type': 'application/json'}, {'key': 'value'}, 5, 10, 400, None),
    ('POST', 'http://test.com', {'content-type': 'application/json'}, {'key': 'value'}, 5, 10, 500, None),
])
def test_execute(method, url, headers, body, interval, timeout, status_code, expected_response, requests_mock):
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
