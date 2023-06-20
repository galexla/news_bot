from peewee import PostgresqlDatabase

from config_data import config

db = PostgresqlDatabase(config.POSTGRES_DB, host=config.POSTGRES_HOST,
                        user=config.POSTGRES_USER,
                        password=config.POSTGRES_PASSWORD,
                        port=config.POSTGRES_PORT)
db.connect(True)
