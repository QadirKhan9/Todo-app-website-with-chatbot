from sqlmodel import Session
from typing import Generator
from ..config.settings import get_settings
from ..db.session import sync_engine

def get_session() -> Generator[Session, None, None]:
    with Session(sync_engine) as session:
        yield session

# Async session generator for async operations
async def get_async_session() -> Generator[Session, None, None]:
    with Session(sync_engine) as session:
        yield session