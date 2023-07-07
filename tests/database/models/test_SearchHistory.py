from datetime import date, datetime

import pytest

from database.models.SearchHistory import SearchHistory


@pytest.fixture
def history_item():
    user_id = '123'
    query = 'test_query'
    date_from = date(2023, 1, 1)
    date_to = date(2023, 1, 2)
    return SearchHistory(user_id=user_id, query=query,
                         date_from=date_from, date_to=date_to)


def test_get_recent(mocker, history_item):
    mock_query = mocker.Mock()
    mock_select = mocker.patch(
        'database.models.SearchHistory.SearchHistory.select', return_value=mock_query)
    SearchHistory.get_recent(history_item.user_id)
    mock_select.assert_called_once()
    mock_query.where.assert_called_once_with(
        SearchHistory.user_id == history_item.user_id)
    mock_query.where.return_value.order_by.assert_called_once_with(
        SearchHistory.entered_date.desc())


def test_add_or_update_new(mocker, history_item):
    mock_get_or_create = mocker.patch.object(SearchHistory, 'get_or_create')
    mock_get_or_create.return_value = (history_item, True)
    SearchHistory.add_or_update(
        history_item.user_id, history_item.query,
        history_item.date_from, history_item.date_to)
    mock_get_or_create.assert_called_with(
        user_id=str(history_item.user_id), query=history_item.query,
        date_from=history_item.date_from, date_to=history_item.date_to)


def test_add_or_update_existing(mocker, history_item):
    mock_get_or_create = mocker.patch.object(SearchHistory, 'get_or_create')
    mock_save = mocker.patch.object(SearchHistory, 'save')
    mock_get_or_create.return_value = (history_item, False)
    SearchHistory.add_or_update(
        history_item.user_id, history_item.query, history_item.date_from, history_item.date_to)
    assert isinstance(history_item.entered_date, datetime)
    mock_save.assert_called()
