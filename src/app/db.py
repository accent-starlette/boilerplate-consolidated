from app.settings import DATABASE_URL
from app.utils.database import Database, metadata

# set db config options
if DATABASE_URL.drivername == "postgresql+asyncpg":
    engine_kwargs = {"pool_size": 5, "max_overflow": 10}
else:
    engine_kwargs = {}

# setup database url
db = Database(DATABASE_URL, engine_kwargs=engine_kwargs)

# import project and external tables so that they all
# live in one place for the migrations to find them
from app.auth import tables  # noqa isort:skip
