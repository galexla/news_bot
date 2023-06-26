from utils.news.important_words import (_get_words_importance, get_all_words,
                                        get_important_words)


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
    expected = {'Qing': 17.531030639740447, 'Xi': 14.79406504557424,
                'hi': 11.287712379549449, 'water': 8.560881162516957}
    actual = _get_words_importance(all_words)
    assert actual == expected

    all_words = []
    expected = {}
    actual = _get_words_importance(all_words)
    assert actual == expected

    all_words = ['water']
    expected = {'water': 11.560881162516957}
    actual = _get_words_importance(all_words)
    assert actual == expected


def test_get_important_words():
    """
    Tests get_important_words() function
    """
    text = 'How long is the present? The answer, Cornell researchers suggest in a new study, depends on your heart. The researchers discovered that our moment-to-moment perception of time is not constant and can expand or contract with each heartbeat. According to Adam K. Anderson, a professor in the Depa.'
    excepted = {'depa': 18.671542913362718, 'heartbeat': 12.06120384974077, 'cornell': 11.994930630321603, 'researchers': 10.673002535434241, 'perception': 10.371235735111734,
                'expand': 9.802285552379209, 'anderson': 9.770436686339867, 'depends': 9.204499011300468, 'constant': 9.170848621858552, 'adam': 9.07048166332878}
    actual = get_important_words([text])
    for word, importance in excepted.items():
        assert actual[word] == importance
