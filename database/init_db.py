from peewee import PostgresqlDatabase

db = PostgresqlDatabase(None)


def init_db(name, **kwargs) -> None:
    """
    Initialize database connection

    :param name: database name
    :type name: str
    :param kwargs: database connection parameters
    :type kwargs: dict
    """
    db.init(name, **kwargs)
    db.connect()


def create_tables() -> None:
    """
    Create tables in the database if they do not exist
    """
    try:
        from database.models.SearchHistory import SearchHistory
    except ImportError:
        print('Could not import models. Is the database initialized?')
        return

    models = [SearchHistory]
    with db:
        # if config.DROP_TABLES:
        #     db.drop_tables(models)
        db.create_tables(models, safe=True)
