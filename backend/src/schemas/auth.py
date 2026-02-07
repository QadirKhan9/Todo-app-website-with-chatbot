from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic.functional_validators import BeforeValidator
from typing import Optional, Union
from datetime import datetime
import uuid
from typing_extensions import Annotated


def uuid_to_str(value: Union[uuid.UUID, str]) -> str:
    """Convert UUID to string."""
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


UUIDToStr = Annotated[str, BeforeValidator(uuid_to_str)]


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        import re
        # Validate that username contains only letters, numbers, and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # At least one uppercase, one lowercase, one digit, one special character
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: UUIDToStr
    username: str
    is_active: bool
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str
    email: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    token: str