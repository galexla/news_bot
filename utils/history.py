from datetime import date, datetime

from database.models.SearchHistory import SearchHistory


# TODO: delete this file


def get(user_id: str):
    return (SearchHistory
            .select()
            .where(SearchHistory.user_id == str(user_id))
            .order_by(SearchHistory.entered_date.desc())
            .limit(10))


def get_by_id(id: str) -> SearchHistory:
    return SearchHistory.get(SearchHistory.id == id)


def add_or_update(user_id: str, query: str,
                  date_from: date, date_to: date) -> None:
    history_item, created = SearchHistory.get_or_create(
        user_id=user_id, query=query, date_from=date_from, date_to=date_to)
    if not created:
        history_item.entered_date = datetime.now()
        history_item.save()
