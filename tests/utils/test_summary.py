from unittest.mock import patch, Mock

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from utils.summary import get_summary, get_summary_percent


@patch('utils.summary.config')
@patch('utils.summary.get_json_value')
@patch('utils.summary.ApiQueryScheduler')
@patch('utils.summary.ApiQuery')
def test_get_summary_percent(mocked_apiquery, mocked_scheduler, mocked_json_value, mocked_config):
    mocked_config.RAPID_API_KEY = 'test_api_key'
    mocked_apiquery.return_value = Mock()
    mocked_scheduler.execute.return_value = {
        'sentences': ['This is a summary.']}
    mocked_json_value.return_value = ['This is a summary.']

    result = get_summary_percent('This is a test string.', 50)

    mocked_apiquery.assert_called_once_with(
        'POST',
        'https://text-analysis12.p.rapidapi.com/summarize-text/api/v1.1',
        headers={'content-type': 'application/json',
                 'X-RapidAPI-Key': 'test_api_key',
                 'X-RapidAPI-Host': 'text-analysis12.p.rapidapi.com'},
        body={'language': 'english', 'summary_percent': 50,
              'text': 'This is a test string.'},
        interval=0.005
    )
    mocked_scheduler.execute.assert_called_once()
    mocked_json_value.assert_called_once_with(
        {'sentences': ['This is a summary.']}, ['sentences'])

    assert result == ['This is a summary.']


def test_get_summary_less_than_n_characters():
    test_string = 'This is a test string.'
    result = get_summary(test_string, 50)
    assert result == [test_string]


@patch('utils.summary.get_summary_percent')
def test_get_summary_more_than_n_characters(mocked_summary_percent):
    test_string = 'This is a test string.'
    mocked_summary_percent.return_value = ['This is a summary.']

    result = get_summary(test_string, 10)

    percent = round(10 / len(test_string) * 100, 3)
    mocked_summary_percent.assert_called_once_with(test_string, percent)
    assert result == ['This is a summary.']
