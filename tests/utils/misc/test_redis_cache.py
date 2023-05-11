import datetime
from utils.misc.redis_cache import _get_ttl, set_summary_input
from unittest.mock import patch, MagicMock, ANY


def test_get_ttl():
    date_to = '2023-04-09T15:11:05'
    ttl = _get_ttl(date_to)
    assert ttl == 3600 * 24 * 90

    date_to = datetime.datetime.utcnow()
    date_to -= datetime.timedelta(hours=2)
    date_to = date_to.strftime('%Y-%m-%dT%H:%M:%S')
    ttl = _get_ttl(date_to)
    assert ttl == 3600 * 3


def test_set_summary_input():
    with patch('utils.misc.redis_cache.redis_connection') as redis_connection_mock:
        set_summary_input('Russia', '2023-04-03T00:00:00',
                          '2023-04-09T23:59:59', 'text')
        redis_connection_mock.set.assert_called_once_with(
            'summary_input:Russia:2023-04-03T00:00:00:2023-04-09T23:59:59',
            'text', ex=3600 * 24 * 90)
    
    with patch('utils.misc.redis_cache.redis_connection') as redis_connection_mock:
        date_to = datetime.datetime.utcnow()
        date_to -= datetime.timedelta(hours=2)
        date_to = date_to.strftime('%Y-%m-%dT%H:%M:%S')
        set_summary_input('Russia', '2023-04-03T00:00:00', date_to, 'text')
        redis_connection_mock.set.assert_called_once_with(
            f'summary_input:Russia:2023-04-03T00:00:00:{date_to}', 'text', ex=3600 * 3)
