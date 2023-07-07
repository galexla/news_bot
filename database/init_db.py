from peewee import PostgresqlDatabase

db = PostgresqlDatabase(None)


def init_db(name, **kwargs):
    db.init(name, **kwargs)
    db.connect()


def create_tables():
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
