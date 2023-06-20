from datetime import date, datetime

from database.models.SearchHistory import SearchHistory


def get(user_id: str):
    return (SearchHistory
            .select()
            .where(SearchHistory.user_id == str(user_id))
            .order_by(SearchHistory.entered_date.desc())
            .limit(10))


def add(user_id: str, query: str, date_from: date, date_to: date) -> None:
    # history_item = SearchHistory(
    #     user_id=user_id, query=query, date_from=date_from, date_to=date_to)
    # # added = history_item.save(force_insert=True)
    # added = history_item.save()
    # pass

    history_item, created = SearchHistory.get_or_create(
        user_id=user_id, query=query, date_from=date_from, date_to=date_to)
    if not created:
        history_item.entered_date = datetime.now()
        history_item.save()
