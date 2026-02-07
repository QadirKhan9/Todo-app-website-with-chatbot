from sqlmodel import SQLModel
from backend.src.database.session import sync_engine
from backend.src.models.user_model import User
from backend.src.models.task import Task

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(sync_engine)

if __name__ == "__main__":
    create_db_and_tables()
