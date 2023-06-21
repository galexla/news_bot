from database.connection.init_db import db
from database.models.SearchHistory import SearchHistory

models = [SearchHistory]
with db:
    # if config.DROP_TABLES:
    # db.drop_tables(models)
    db.create_tables(models, safe=True)
