from copy import copy
from typing import AsyncIterator

import pytest
import sqlalchemy as sa
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from starlette.config import environ

environ["TESTING"] = "TRUE"

from app.auth.tables import User

from app.db import db  # noqa isort:skip
from app.main import app  # noqa isort:skip
from app.settings import DATABASE_URL  # noqa isort:skip
from app.utils.testing import create_user  # noqa isort:skip


def database_exists():
    url = copy(DATABASE_URL)
    db_name = url.database
    url = url.set(database="postgres")
    engine = sa.create_engine(str(url))

    def get_scalar_result(engine, sql):
        result_proxy = engine.execute(sql)
        result = result_proxy.scalar()
        result_proxy.close()
        engine.dispose()
        return result

    text = "SELECT 1 FROM pg_database WHERE datname='%s'" % db_name
    return bool(get_scalar_result(engine, text))


def create_database():
    url = copy(DATABASE_URL)
    db_name = url.database
    url = url.set(database="postgres")
    engine = sa.create_engine(str(url))
    engine.raw_connection().set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    text = """
        CREATE DATABASE %(db_name)s ENCODING 'utf8'
    """ % {
        "db_name": db_name
    }
    result_proxy = engine.execute(text)
    result_proxy.close()
    engine.dispose()


def drop_database():
    url = copy(DATABASE_URL)
    db_name = url.database
    url = url.set(database="postgres")
    engine = sa.create_engine(str(url))

    connection = engine.connect()
    connection.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Disconnect all users from the database we are dropping.
    version = connection.dialect.server_version_info
    pid_column = "pid" if (version >= (9, 2)) else "procpid"
    text = """
    SELECT pg_terminate_backend(pg_stat_activity.%(pid_column)s)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '%(database)s'
        AND %(pid_column)s <> pg_backend_pid();
    """ % {
        "pid_column": pid_column,
        "database": db_name,
    }
    connection.execute(text)

    # Drop the database.
    text = f"DROP DATABASE {db_name}"
    connection.execute(text)
    connection.close()
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    if database_exists():
        drop_database()
    create_database()


@pytest.fixture(scope="function", autouse=True)
async def database():
    await db.create_all()
    yield db
    await db.drop_all()


@pytest.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac


@pytest.fixture()
async def user():
    user = await create_user("test@example.com", "pass", "Test", "User")
    # refetch the user with scopes
    qs = (
        sa.select(User)
        .where(User.id == user.id)
        .options(sa.orm.selectinload(User.scopes))
    )
    result = await User.execute(qs)
    return result.scalar()


@pytest.fixture()
async def login(user, client):
    url = app.url_path_for("auth:login")
    await client.post(url, data={"email": user.email, "password": "pass"})
