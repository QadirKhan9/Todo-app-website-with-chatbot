from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
import sqlite3
import os
import logging
from typing import AsyncGenerator
from ..config.settings import get_settings

# Configure SQLAlchemy logging to reduce noise
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.orm').setLevel(logging.ERROR)

# Get database URL from settings
settings = get_settings()

# Determine if we're using PostgreSQL (for Neon)
is_postgres = settings.DATABASE_URL.startswith("postgresql")

if is_postgres:
    # Use async engine for PostgreSQL (Neon)
    DATABASE_URL_ASYNC = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        DATABASE_URL_ASYNC,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,  # Disable SQL logging for cleaner output
        logging_name="cohere_chat_async"  # Custom name for easier filtering if needed
    )
    # Sync engine for sync operations if needed
    from sqlalchemy import create_engine
    sync_engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=False,  # Disable SQL logging for cleaner output
        logging_name="cohere_chat_sync"  # Custom name for easier filtering if needed
    )
else:
    # Use regular sync engine for SQLite
    from sqlalchemy import create_engine
    sync_engine = create_engine(
        settings.DATABASE_URL,
        echo=False,  # Disable SQL logging for cleaner output
        pool_pre_ping=True,
        logging_name="cohere_chat_sync"  # Custom name for easier filtering if needed
    )
    engine = None  # No async engine for SQLite


def create_db_and_tables():
    """
    Creates the database and all tables defined in the models.
    This should be called when the application starts.
    """
    # Import all models here to register them with SQLModel
    from ..models.user_model import User  # noqa: F401
    from ..models.conversation import Conversation  # noqa: F401
    from ..models.message import Message  # noqa: F401
    from ..models.agent_response import AgentResponse  # noqa: F401
    from ..models.tool_call import ToolCall  # noqa: F401
    from ..models.todo import Todo  # noqa: F401

    # Create all tables using sync engine
    SQLModel.metadata.create_all(sync_engine)


@event.listens_for(sync_engine, "connect") if 'sync_engine' in locals() else None
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Sets SQLite pragmas for better performance and concurrency.
    This is only applied if using SQLite.
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Session generators
from sqlmodel import Session

def get_session():
    """Get a sync database session"""
    with Session(sync_engine) as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session"""
    # Use the appropriate engine based on the database type
    if engine is not None:
        # Using PostgreSQL with async engine
        async with AsyncSession(engine) as session:
            yield session
    else:
        # Using SQLite, fall back to sync engine wrapped in async context
        # This is not ideal but maintains compatibility
        from sqlmodel import Session
        with Session(sync_engine) as session:
            yield session