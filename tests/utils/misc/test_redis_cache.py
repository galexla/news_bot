from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, call, patch

import pytest

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    import utils.misc.redis_cache as cache


def test_exists():
    with patch('utils.misc.redis_cache.redis_connection') as redis_connection_mock:
        key = '1:2:3:text'
        cache.exists(key)
        redis_connection_mock.exists.assert_called_once_with(key)


def test_all_exist():
    with patch('utils.misc.redis_cache.redis_connection') as redis_connection_mock:
        prefixes = ['1', '2', '3']
        query, date_from, date_to = 'text', date(2020, 1, 1), date(2020, 2, 27)
        cache.all_exist(prefixes, query, date_from, date_to)
        tail = f'{query}:2020-01-01T00:00:00:2020-02-27T23:59:59'
        redis_connection_mock.exists.assert_has_calls((
            call(f'1:{tail}'),
            call().__bool__(),
            call(f'2:{tail}'),
            call().__bool__(),
            call(f'3:{tail}'),
            call().__bool__(),
        ))


def test_key():
    assert cache.key(
        'summary', 'Russia', '2023-04-03T00:00:00', '2023-04-09T23:59:59') == \
        'summary:Russia:2023-04-03T00:00:00:2023-04-09T23:59:59'
    assert cache.key('', '', '') == '::'
    assert cache.key('text', 'Ecology') == 'text:Ecology'
    assert cache.key('text') == 'text'


@pytest.mark.parametrize('prefix, search_query, date_from, date_to, result', [
    ('prefix1', 'Ecology', date(2023, 4, 3), date(2023, 4, 9),
     'prefix1:Ecology:2023-04-03T00:00:00:2023-04-09T23:59:59'),
    ('prefix2', '', date(2020, 1, 1), date(2020, 2, 27),
     'prefix2::2020-01-01T00:00:00:2020-02-27T23:59:59'),
    ('', '', date(2023, 4, 3), date(2023, 4, 9),
     '::2023-04-03T00:00:00:2023-04-09T23:59:59'),
])
def test_key_query(prefix: str, search_query: str, date_from: date, date_to: date, result: str):
    assert cache.key_query(prefix, search_query, date_from, date_to) == result


def test_get():
    with patch('utils.misc.redis_cache.redis_connection') as redis_connection_mock:
        key = 'summary_input:Russia:2023-04-03T00:00:00:2023-04-09T23:59:59'
        cache.get(key)
        redis_connection_mock.get.assert_called_once_with(key)


def test__cast_type():
    assert cache._cast_type(None) is None
    assert cache._cast_type('123') == 123
    assert cache._cast_type('123.45') == 123.45
    assert cache._cast_type('{"a": 1}') == {'a': 1}
    assert cache._cast_type('abc') == 'abc'


def test_get_ttl():
    with patch('utils.misc.redis_cache.redis_connection') as redis_connection_mock:
        key = 'a:b:c:d'
        cache.get_ttl(key)
        redis_connection_mock.ttl.assert_called_once_with(key)


@ pytest.mark.parametrize('prefix, search_query, date_from, date_to, text, ttl, expected_key', [
    ('summary_input', 'Russia', '2023-04-03T00:00:00', '2023-04-09T23:59:59', 'text1',
     100, 'summary_input:Russia:2023-04-03T00:00:00:2023-04-09T23:59:59'),
    ('summary', 'Ecology', '2023-04-09T00:00:00', '2023-04-09T23:59:59', 'text2',
     3000, 'summary:Ecology:2023-04-09T00:00:00:2023-04-09T23:59:59'),
    ('', '', '', '', 'text3', 200, ':::'),
])
def test_set(prefix, search_query, date_from, date_to, text, ttl, expected_key):
    with patch('utils.misc.redis_cache.redis_connection') as redis_connection_mock:
        key = cache.key(prefix, search_query, date_from, date_to)
        cache.set(key, text, ex=ttl)
        redis_connection_mock.set.assert_called_once_with(key, text, ex=ttl)


def test_get_set():
    func = MagicMock(return_value=3)
    with patch('utils.misc.redis_cache.get') as get_mock, \
            patch('utils.misc.redis_cache.set') as set_mock, \
            patch('utils.misc.redis_cache.redis_connection.exists') as exists_mock:
        key, ttl = 'a:b:c:d', 1000
        cache.get_set(key, ttl, func, 'text')
        exists_mock.assert_called_once_with(key)
        get_mock.assert_called_once_with(key)

    with patch('utils.misc.redis_cache.get') as get_mock, \
            patch('utils.misc.redis_cache.set') as set_mock, \
            patch('utils.misc.redis_cache.redis_connection.exists', return_value=False) as exists_mock:
        key, ttl = 'a:b:c:d', 1000
        cache.get_set(key, ttl, func, 'text')
        exists_mock.assert_called_once_with(key)
        set_mock.assert_called_once_with(key, 3, ex=ttl)


def test__get_str_for_log():
    assert cache._get_str_for_log('abc') == 'abc'
    assert cache._get_str_for_log('text' * 26) == 'text' * 25 + '...'
    assert cache._get_str_for_log({'a': 1}) == 'count=1'
    assert cache._get_str_for_log(123) == 123
    assert cache._get_str_for_log(123.45) == 123.45
    assert cache._get_str_for_log(None) is None


def test_calc_ttl():
    FRESH_RECORD_TTL = 3600 * 3
    OLD_RECORD_TTL = 3600 * 24 * 7

    datetime_to = datetime(2023, 4, 9, 15, 11, 5)
    assert cache.calc_ttl(datetime_to) == OLD_RECORD_TTL

    datetime_to = datetime.utcnow()
    datetime_to -= timedelta(hours=2)
    assert cache.calc_ttl(datetime_to) == FRESH_RECORD_TTL
