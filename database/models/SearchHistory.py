from datetime import date, datetime

from peewee import AutoField, CharField, DateField, DateTimeField, Model

from database.connection.init_db import db


class SearchHistory(Model):
    id = AutoField()
    user_id = CharField(max_length=255)
    entered_date = DateTimeField(default=datetime.utcnow)
    query = CharField(max_length=255)
    date_from = DateField()
    date_to = DateField()

    class Meta:
        database = db
        indexes = (
            (('user_id', 'query', 'date_from', 'date_to'), True),
            (('user_id',), False),
            (('entered_date',), False)
        )

    @classmethod
    def get_recent(cls, user_id: str | int):
        return (cls
                .select()
                .where(cls.user_id == str(user_id))
                .order_by(cls.entered_date.desc())
                .limit(10))

    @classmethod
    def add_or_update(cls, user_id: str | int, query: str,
                      date_from: date, date_to: date) -> None:
        history_item, created = cls.get_or_create(
            user_id=str(user_id), query=query,
            date_from=date_from, date_to=date_to)
        if not created:
            history_item.entered_date = datetime.now()
            history_item.save()
