import asyncio
from copy import copy
from typing import AsyncIterator

import pytest
import sqlalchemy as sa
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.config import environ

environ["TESTING"] = "TRUE"

from app.auth.tables import User

from app.main import app  # noqa isort:skip
from app.settings import DATABASE_URL  # noqa isort:skip
from app.utils.database import Database  # noqa isort:skip
from app.utils.testing import create_user  # noqa isort:skip


def get_db_maintenance_url():
    url = copy(DATABASE_URL)
    url = url.set(database="postgres")
    return url


async def database_exists():
    url = get_db_maintenance_url()
    engine = create_async_engine(str(url))

    async def get_scalar_result(engine, sql):
        async with engine.connect() as conn:
            result_proxy = await conn.execute(sql)
            result = result_proxy.scalar()
        await engine.dispose()
        return result

    text = sa.text(
        """
        SELECT 1 FROM pg_database WHERE datname='%(db_name)s'
    """
        % {"db_name": DATABASE_URL.database}
    )
    return bool(await get_scalar_result(engine, text))


async def create_database():
    url = get_db_maintenance_url()
    engine = create_async_engine(str(url), isolation_level="AUTOCOMMIT")

    text = sa.text(
        """
        CREATE DATABASE %(db_name)s ENCODING 'utf8'
    """
        % {"db_name": DATABASE_URL.database}
    )
    async with engine.connect() as conn:
        await conn.execute(text)
    await engine.dispose()


async def drop_database():
    url = get_db_maintenance_url()
    engine = create_async_engine(str(url), isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:

        # Disconnect all users from the database we are dropping.
        version = conn.dialect.server_version_info
        pid_column = "pid" if (version >= (9, 2)) else "procpid"
        text = sa.text(
            """
        SELECT pg_terminate_backend(pg_stat_activity.%(pid_column)s)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '%(db_name)s'
            AND %(pid_column)s <> pg_backend_pid();
        """
            % {
                "pid_column": pid_column,
                "db_name": DATABASE_URL.database,
            }
        )
        await conn.execute(text)

        # Drop the database.
        text = sa.text(
            """
            DROP DATABASE %(db_name)s
        """
            % {"db_name": DATABASE_URL.database}
        )
        await conn.execute(text)

    await engine.dispose()


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    if await database_exists():
        await drop_database()
    await create_database()


@pytest.fixture(scope="function", autouse=True)
async def database():
    db = Database(DATABASE_URL)
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
