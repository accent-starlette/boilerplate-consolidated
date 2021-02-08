import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from starlette.exceptions import HTTPException

metadata = sa.MetaData()


@as_declarative(metadata=metadata)
class ModelBase:
    metadata: sa.MetaData = metadata
    session: AsyncSession = None

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    async def get(cls, ident):
        qs = sa.select(cls).where(cls.id == ident)
        results = await cls.session.execute(qs)
        return results.scalars().first()

    @classmethod
    async def get_or_404(cls, ident):
        result = await cls.get(ident)
        if not result:
            raise HTTPException(status_code=404)
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}, id={self.id}>"

    def __str__(self):
        return self.__repr__()

    id = sa.Column(sa.Integer, primary_key=True)

    async def save(self) -> None:
        """ save the current instance """

        async with self.session.begin_nested():
            self.session.add(self)

        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete(self) -> None:
        """ delete the current instance """

        async with self.session.begin_nested():
            self.session.delete(self)

        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def refresh_from_db(self) -> None:
        """ Refresh the current instance from the database """

        await self.session.refresh(self)


class Database:
    engine: AsyncEngine = None
    session: AsyncSession = None

    def __init__(self, url: str, engine_kwargs: dict = {}) -> None:
        # configure the engine
        self.engine = create_async_engine(str(url), **engine_kwargs)
        self.session = AsyncSession(bind=self.engine)
        # configue base attrs
        ModelBase.session = self.session

    async def create_all(self) -> None:
        # create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def drop_all(self) -> None:
        # close the open session
        await self.session.close()
        # drop all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)

    async def truncate_all(self) -> None:
        async with self.engine.connect() as conn:
            trans = await conn.begin()
            for table in reversed(metadata.sorted_tables):
                try:
                    await conn.execute(table.delete())
                except:
                    pass
            await trans.commit()
