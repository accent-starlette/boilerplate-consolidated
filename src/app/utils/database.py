import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker
from starlette.exceptions import HTTPException

metadata = sa.MetaData()


@as_declarative(metadata=metadata)
class ModelBase:
    metadata: sa.MetaData = metadata
    db: "Database"

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    async def execute(cls, qs):
        async with cls.db.session() as session:
            async with session.begin():
                return await session.execute(qs)

    @classmethod
    async def get(cls, ident):
        qs = sa.select(cls).where(cls.id == ident)
        results = await cls.execute(qs)
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

        async with self.db.session() as session:
            async with session.begin_nested():
                session.add(self)

            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def delete(self) -> None:
        """ delete the current instance """

        async with self.db.session() as session:
            async with session.begin_nested():
                session.delete(self)

            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e


class Database:
    engine: AsyncEngine

    def __init__(self, url: str, engine_kwargs: dict = {}) -> None:
        # configure the engine
        self.engine = create_async_engine(str(url), **engine_kwargs)
        # configue base attrs
        ModelBase.db = self

    @property
    def session(self) -> sessionmaker:
        return sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def create_all(self) -> None:
        # create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def drop_all(self) -> None:
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
