from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from utils import Singleton
from database.models import Base


DATABASE_URL = (
    'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database_name}'
)


class Database(Singleton):
    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: str,
        database_name: str
    ) -> None:
        url = DATABASE_URL.format(
            user=user,
            password=password,
            host=host,
            port=port,
            database_name=database_name
        )
        self.__engine = create_async_engine(url)
        self.session = sessionmaker(
            self.__engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def init_models(self):
        async with self.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.__engine.dispose()
