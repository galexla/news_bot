import datetime
from utils.misc.redis_cache import get_ttl, set_summary_input
from unittest.mock import patch


def test_get_ttl():
    datetime_to = '2023-04-09T15:11:05'
    ttl = get_ttl(datetime_to)
    assert ttl == 3600 * 24 * 7

    datetime_to = datetime.datetime.utcnow()
    datetime_to -= datetime.timedelta(hours=2)
    datetime_to = datetime_to.strftime('%Y-%m-%dT%H:%M:%S')
    ttl = get_ttl(datetime_to)
    assert ttl == 3600 * 3


def test_set_summary_input():
    with patch('utils.misc.redis_cache.redis_connection') as redis_connection_mock:
        set_summary_input('Russia', '2023-04-03T00:00:00',
                          '2023-04-09T23:59:59', 'text')
        redis_connection_mock.set.assert_called_once_with(
            'summary_input:Russia:2023-04-03T00:00:00:2023-04-09T23:59:59',
            'text', ex=3600 * 24 * 7)
    
    with patch('utils.misc.redis_cache.redis_connection') as redis_connection_mock:
        datetime_to = datetime.datetime.utcnow()
        datetime_to -= datetime.timedelta(hours=2)
        datetime_to = datetime_to.strftime('%Y-%m-%dT%H:%M:%S')
        set_summary_input('Russia', '2023-04-03T00:00:00', datetime_to, 'text')
        redis_connection_mock.set.assert_called_once_with(
            f'summary_input:Russia:2023-04-03T00:00:00:{datetime_to}', 'text', ex=3600 * 3)
