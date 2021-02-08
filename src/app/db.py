from app.settings import DATABASE_URL
from app.utils.database import Database, metadata

# set db config options
if DATABASE_URL.drivername == "psycopg2":
    engine_kwargs = {"pool_size": 20, "max_overflow": 0}
else:
    engine_kwargs = {}

# setup database url
db = Database(DATABASE_URL, engine_kwargs=engine_kwargs)

# print all running queries to the console
# see https://docs.sqlalchemy.org/en/13/core/engines.html
# db.engine.echo = True

# import project and external tables so that they all
# live in one place for the migrations to find them
from app.auth import tables  # noqa isort:skip
