from typing import AsyncGenerator
from contextlib import asynccontextmanager
from .config import settings
import asyncio
from ..db.session import sync_engine


def get_session():
    """Get a database session"""
    from sqlmodel import Session
    with Session(sync_engine) as session:
        yield session


async def get_async_session():
    """Get an async database session"""
    # For now, using synchronous session in async context
    # In a real implementation, you would use an async database driver
    from sqlmodel import Session
    with Session(sync_engine) as session:
        yield session