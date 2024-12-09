import contextlib
import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from conf.config import app_config

logger = logging.getLogger("uvicorn.error")

class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url, echo=True)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception('Session maker not defined')
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as error:
            logger.error(f"Error when working with the database: {error}")
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(app_config.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session
