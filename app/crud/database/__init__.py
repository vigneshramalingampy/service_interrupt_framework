import logging
from asyncio import current_task
from contextlib import asynccontextmanager
from functools import wraps
from typing import Generator, Optional

from alembic import command
from sqlalchemy import NullPool
from sqlalchemy.exc import (
    DatabaseError,
    OperationalError,
    ProgrammingError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.config.migration_config import config
from app.sql.base import Base


class PostgresSQL:
    def __init__(self):
        self.connection_url: str = settings.database_url
        self.engine: AsyncEngine = create_async_engine(
            self.connection_url,
            poolclass=NullPool,
            echo=settings.debug,
            future=True,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
            class_=AsyncSession,
        )
        self.AsyncScopedSession: async_scoped_session = async_scoped_session(
            self.session_factory,
            scopefunc=current_task,
        )


database: PostgresSQL = PostgresSQL()


@asynccontextmanager
async def get_session() -> Generator[async_scoped_session, None, None]:
    async_session: Optional[async_scoped_session] = database.AsyncScopedSession()
    try:
        yield async_session
    except (SQLAlchemyError, OperationalError, DatabaseError, ProgrammingError) as exception:
        logging.error(f"Error while creating session: {exception}")
        await async_session.rollback()
        raise exception
    finally:
        if session is not None:
            await async_session.close()


def session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with get_session() as db_session:
            return await func(db_session, *args, **kwargs)

    return wrapper


async def initialize_database():
    async with database.engine.begin() as database_connection:
        connection: AsyncConnection = database_connection
        await connection.run_sync(Base.metadata.create_all)
        await connection.run_sync(run_upgrade, config)


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


def run_revision(connection, cfg):
    cfg.attributes["connection"] = connection
    command.revision(cfg, autogenerate=True)
