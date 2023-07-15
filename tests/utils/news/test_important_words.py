from unittest.mock import patch


with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from utils.news.important_words import (_get_words_importance,
                                            get_all_words, get_important_words)


def test_get_all_words():
    """
    Tests get_all_words() function
    """
    news = ['Hi, Xi Jinping!', 'Qing water']
    expected = ['hi', 'xi', 'jinping', 'qing', 'water']
    actual = get_all_words(news)
    assert actual == expected

    news = []
    expected = []
    actual = get_all_words(news)
    assert actual == expected


def test_get_words_importance():
    """
    Tests _get_words_importance() function
    """
    all_words = ['hi', 'hi', 'Xi', 'Xi', 'Xi', 'Qing', 'Qing', 'water']
    expected = {'hi': 7.8244459312774595, 'Xi': 10.254499674775916,
                'Qing': 12.151589740237444, 'water': 5.93659514377329}
    actual = _get_words_importance(all_words)
    assert actual == expected

    all_words = []
    expected = {}
    actual = _get_words_importance(all_words)
    assert actual == expected

    all_words = ['water']
    expected = {'water': 8.013723128149687}
    actual = _get_words_importance(all_words)
    assert actual == expected


def test_get_important_words():
    """
    Tests get_important_words() function
    """
    text = 'How long is the present? The answer, Cornell researchers suggest in a new study, depends on your heart. The researchers discovered that our moment-to-moment perception of time is not constant and can expand or contract with each heartbeat. According to Adam K. Anderson, a professor in the Depa.'
    excepted = {'depa': 12.942129722100923, 'heartbeat': 8.360423415466789, 'cornell': 8.314497317656889, 'researchers': 7.398573928655951, 'perception': 7.189547524600555,
                'expand': 6.795545968061798, 'anderson': 6.773494988107069, 'depends': 6.381766104950554, 'constant': 6.35848136394146, 'adam': 6.289037065455538}
    actual = get_important_words([text])
    for word, importance in excepted.items():
        assert actual[word] == importance
