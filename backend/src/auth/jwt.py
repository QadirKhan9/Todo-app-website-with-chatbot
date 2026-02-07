from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from ..config.settings import get_settings
from ..utils.exceptions import AuthenticationError, AuthorizationError


# Initialize security context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class TokenData(BaseModel):
    """
    Data contained in a JWT token.
    """
    user_id: str
    expires_at: datetime


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hash for a plain password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with the provided data.
    """
    settings = get_settings()
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode a JWT access token and return the token data.
    """
    settings = get_settings()
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        expires_at: float = payload.get("exp", 0)
        
        if user_id is None or expires_at is None:
            return None
        
        token_data = TokenData(user_id=user_id, expires_at=datetime.fromtimestamp(expires_at))
        return token_data
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to get the current user from the JWT token in the Authorization header.
    """
    settings = get_settings()
    
    try:
        token_data = decode_access_token(credentials.credentials)
        if token_data is None:
            raise AuthenticationError("Could not validate credentials")
        
        if token_data.expires_at < datetime.utcnow():
            raise AuthenticationError("Token has expired")
        
        return token_data.user_id
    except JWTError:
        raise AuthenticationError("Could not validate credentials")


def require_same_user(current_user_id: str = Depends(get_current_user)):
    """
    Dependency to ensure the current user has access to resources owned by the same user.
    This is used for conversation access control.
    """
    def check_user(resource_user_id: str) -> bool:
        if current_user_id != resource_user_id:
            raise AuthorizationError("Not authorized to access this resource")
        return True
    return check_user