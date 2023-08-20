from datetime import date, datetime

from peewee import AutoField, CharField, DateField, DateTimeField, Model

from database.init_db import db


class SearchHistory(Model):
    """
    Search history model

    Attributes:
        id (int): id
        user_id (str): user id
        entered_date (datetime): entered date
        query (str): search query
        date_from (date): date from
        date_to (date): date to
    """

    id = AutoField()
    user_id = CharField(max_length=255)
    entered_date = DateTimeField(default=datetime.utcnow)
    query = CharField(max_length=255)
    date_from = DateField()
    date_to = DateField()

    class Meta:
        """
        Meta class

        Attributes:
            database (Database): database
            indexes (tuple[tuple]): indexes
        """

        database = db
        indexes = (
            (('user_id', 'query', 'date_from', 'date_to'), True),
            (('user_id',), False),
            (('entered_date',), False),
        )

    @classmethod
    def get_recent(cls, user_id: str | int) -> list['SearchHistory']:
        """
        Gets recent search history (last 5 items)

        :param user_id: user id
        :type user_id: str | int
        :return: recent search history
        :rtype: list[SearchHistory]
        """
        return (
            cls.select()
            .where(cls.user_id == str(user_id))
            .order_by(cls.entered_date.desc())
            .limit(5)
        )

    @classmethod
    def add_or_update(
        cls, user_id: str | int, query: str, date_from: date, date_to: date
    ) -> None:
        """
        Adds or updates search history item

        :param user_id: user id
        :type user_id: str | int
        :param query: query
        :type query: str
        :param date_from: date from
        :type date_from: date
        :param date_to: date to
        :type date_to: date
        """
        history_item, created = cls.get_or_create(
            user_id=str(user_id),
            query=query,
            date_from=date_from,
            date_to=date_to,
        )
        if not created:
            history_item.entered_date = datetime.now()
            history_item.save()
