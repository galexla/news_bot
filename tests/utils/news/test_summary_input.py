from utils.news.summary_input import _clean_news_text, _join_news


def test__clean_news_text():
    """
    Tests _clean_news_text function
    """
    symbols = '\r\n\n [] ( ) : ; , { }| \t'
    assert _clean_news_text('') == ''
    assert _clean_news_text('asd') == 'asd.'
    assert _clean_news_text('asd.') == 'asd.'
    assert _clean_news_text('asd!') == 'asd!'
    assert _clean_news_text(symbols + 'asd?' + symbols) == 'asd?'
    assert _clean_news_text(symbols + 'asd' + symbols) == 'asd.'


def test__join_news():
    """
    Tests _join_news function
    """
    news = [
        {'text': 'text1'},
        {'text': 'text2'},
        {'text': 'text3'},
    ]
    assert _join_news(news, 'text') == 'text1.\ntext2.\ntext3.'
    assert _join_news([], 'text') == ''
    assert _join_news(news, '') == ''
