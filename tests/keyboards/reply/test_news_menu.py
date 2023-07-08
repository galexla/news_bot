import pytest
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.reply import news_menu


@pytest.fixture
def news_items():
    news_list = []
    for i in range(1, 3):
        news_item = {'id': i, 'title': f'title{i}'}
        news_list.append(news_item)
    return news_list


def test_main(news_items):
    result = news_menu.main(news_items)

    assert isinstance(result, InlineKeyboardMarkup)
    for i, item in enumerate(news_items, start=1):
        assert isinstance(result.keyboard[i - 1][0], InlineKeyboardButton)
        assert result.keyboard[i - 1][0].text == item['title'].strip()
        assert result.keyboard[i - 1][0].callback_data == f'news_{i}'


def test_news_item():
    news_id = '1'
    url = 'test_url'
    result = news_menu.news_item(news_id, url)

    assert isinstance(result, InlineKeyboardMarkup)
    assert isinstance(result.keyboard[0][0], InlineKeyboardButton)
    assert result.keyboard[0][0].text == 'Get summary'
    assert result.keyboard[0][0].callback_data == f'summary_{news_id}'
    assert isinstance(result.keyboard[1][0], InlineKeyboardButton)
    assert result.keyboard[1][0].text == 'Read the article'
    assert result.keyboard[1][0].url == url
