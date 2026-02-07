from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .todo import Todo


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, nullable=False)  # Added username field
    role: str = Field(default="USER", max_length=5)  # Role field that exists in DB
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = Field(default=None)
    email_verified: bool = Field(default=False)
    hashed_password: str = Field(nullable=False)  # Added for database storage

    # Relationships
    todos: list["Todo"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str
    email: str
    username: str  # Added username field


class UserUpdate(SQLModel):
    email: Optional[str] = None
    username: Optional[str] = None  # Added username field
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None


class UserRead(UserBase):
    id: uuid.UUID
    username: str  # Added username field
    created_at: datetime
    updated_at: datetime
    is_active: bool
    last_login: Optional[datetime]
    email_verified: bool