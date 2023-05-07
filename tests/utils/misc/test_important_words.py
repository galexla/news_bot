from utils.misc.important_words import (_get_all_words, _get_words_importance,
                                        get_important_words)


def test_get_words_importance():
    """
    Tests _get_words_importance() function
    """
    all_words = ['hi', 'hi', 'Xi', 'Xi', 'Xi', 'Qing', 'Qing', 'water']
    expected = {'Qing': 189393.9393939394, 'Xi': 28409.090909090908,
                'hi': 2500.0, 'water': 377.64350453172204}
    actual = _get_words_importance(all_words)
    assert actual == expected

    all_words = []
    expected = {}
    actual = _get_words_importance(all_words)
    assert actual == expected

    all_words = ['water']
    expected = {'water': 3021.1480362537764}
    actual = _get_words_importance(all_words)
    assert actual == expected

    # TODO: move file to tests/data?
    filename = '/home/alexander/_dev/educ/skillbox/python_basic_diploma/news_text_descr.txt'
    with open(filename, 'r') as file:
        text = file.read()
    excepted = {
        'baos': 43960.87482140894,
        'algal': 1211.1669593653485,
        'heartbeat': 126.81021583098733
    }
    actual = get_important_words([{'text': text}], text_keys=['text'])
    for word, importance in excepted.items():
        assert actual[word] == importance


def test_get_all_words():
    """
    Tests _get_all_words() function
    """
    news = [{'text': 'Hi, Xi Jinping!'}, {'text': 'Qing water'}]
    text_keys = 'text'
    expected = ['hi', 'xi', 'jinping', 'qing', 'water']
    actual = _get_all_words(news, text_keys)
    assert actual == expected

    news = []
    text_keys = ['text', 'a']
    expected = []
    actual = _get_all_words(news, text_keys)
    assert actual == expected
