import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from app.utils.database import ModelBase


class SomeModel(ModelBase):
    name = sa.Column(sa.String(50), unique=True)


@pytest.mark.asyncio
async def test_database(database):

    # connects ok
    async with database.engine.begin() as conn:

        def tbls(conn):
            return sa.inspect(conn).get_table_names()

        # can create tables
        await database.create_all()
        assert "user" in await conn.run_sync(tbls)

        # can drop tables
        await database.drop_all()
        assert [] == await conn.run_sync(tbls)


@pytest.mark.asyncio
async def test_declarative_base__save(database):
    await database.create_all()

    user = SomeModel(name="ted")
    await user.save()

    qs = sa.select(SomeModel).where(SomeModel.name == "ted")
    result = await SomeModel.execute(qs)
    assert result.scalars().first().id == user.id


@pytest.mark.asyncio
async def test_declarative_base__delete(database):
    await database.create_all()

    user = SomeModel(name="ted")
    await user.save()

    await user.delete()

    qs = sa.select(SomeModel).where(SomeModel.name == "ted")
    result = await SomeModel.execute(qs)
    assert result.scalars().first() is None


@pytest.mark.asyncio
async def test_declarative_base__repr(database):
    await database.create_all()

    user = SomeModel()

    assert user.__tablename__ == "somemodel"
    assert repr(user) == f"<SomeModel, id={user.id}>"
    assert str(user) == f"<SomeModel, id={user.id}>"


@pytest.mark.asyncio
async def test_declarative_base__get(database):
    await database.create_all()

    user = SomeModel(name="ted")
    await user.save()

    # get
    assert (await SomeModel.get(user.id)).id == user.id

    # get is none
    assert await SomeModel.get(1000) is None


@pytest.mark.asyncio
async def test_declarative_base__get_or_404(database):
    await database.create_all()

    user = SomeModel(name="ted")
    await user.save()

    # get_or_404
    assert await SomeModel.get_or_404(user.id)

    # get_or_404 raises http exception when no result found
    with pytest.raises(HTTPException) as e:
        await SomeModel.get_or_404(1000)
    assert e.value.status_code == 404
