from datetime import datetime

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
