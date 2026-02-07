"""
Database migration script for Todo AI Chatbot - MCP Server Tools

This script creates the initial database schema for the User and Task tables.
"""

from sqlmodel import SQLModel
from sqlalchemy import create_engine, text
from backend.src.models.user_model import User
from backend.src.models.task import Task
from backend.src.database.session import DATABASE_URL

def create_initial_schema():
    """Create the initial database schema."""
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    # Create indexes
    with engine.connect() as conn:
        # Index on tasks.user_id for efficient user-scoped queries
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks (user_id);"))
        except Exception as e:
            # Index already exists, continue
            pass

        # Index on tasks.status for efficient status-based queries
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);"))
        except Exception as e:
            # Index already exists, continue
            pass

        # Composite index on (user_id, status) for common combined queries
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_user_id_status ON tasks (user_id, status);"))
        except Exception as e:
            # Index already exists, continue
            pass

        conn.commit()

if __name__ == "__main__":
    create_initial_schema()