from unittest.mock import patch

with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from utils.misc import get_json_value


def test_get_json_value():
    assert get_json_value(None, None) is None
    assert get_json_value({'a': {'b': 'c'}}, ()) is None
    assert get_json_value(None, ('a', 'b')) is None

    assert get_json_value({'a': {'b': 'c'}}, ('a', 'b')) == 'c'
    assert get_json_value({'a': {'b': 'c'}}, ['a']) == {'b': 'c'}
    assert get_json_value(['ddd', {'b': 'c'}], [1, 'b']) == 'c'
    json = {'app_version': 'v1.1', 'time_taken': 0.4565136432647705,
            'msg': 'summarization successful', 'ok': True, 'sentence_count': 7,
            'summary': 'aaa', 'sentences': ['a', 'b', 'c', 'd', 'e', 'f', 'g']}
    assert get_json_value(json, ('summary',)) == 'aaa'

    assert get_json_value({'ddd': {'b': 'c'}}, ('a')) is None
    assert get_json_value([], [1, 'b']) is None
    assert get_json_value({}, 'a') is None
    assert get_json_value({(1, 2): 'c'}, [(1, 2)]) is None
