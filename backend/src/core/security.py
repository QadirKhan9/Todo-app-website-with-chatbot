import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from ..config.settings import get_settings
settings = get_settings()


# Configure logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hash for the given password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    try:
        logger.debug(f"Creating access token with data: {to_encode}")
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug(f"Encoded JWT: {encoded_jwt[:50] if encoded_jwt else 'None'}...")

        # Ensure the token is not empty
        if not encoded_jwt:
            logger.error("Failed to generate access token - result was empty")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate access token"
            )

        logger.info(f"Successfully created access token for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate access token: {str(e)}"
        )


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT refresh token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    try:
        logger.debug(f"Creating refresh token with data: {to_encode}")
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug(f"Encoded refresh JWT: {encoded_jwt[:30] if encoded_jwt else 'None'}...")

        # Ensure the token is not empty
        if not encoded_jwt:
            logger.error("Failed to generate refresh token - result was empty")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate refresh token"
            )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate refresh token: {str(e)}"
        )


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token
    """
    logger.debug(f"Verifying token: {token[:30] if token else 'None'}...")

    # Check if token is literally "undefined" (common frontend issue)
    if token == "undefined":
        logger.warning("Received 'undefined' as token value - likely a frontend issue with token storage/retrieval")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No valid authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate token format before attempting to decode
    if not token or token.count(".") != 2:
        logger.warning(f"Invalid token format: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not in JWT format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        logger.debug(f"Attempting to decode token with SECRET_KEY: {settings.SECRET_KEY[:10]}... and ALGORITHM: {settings.ALGORITHM}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug(f"Successfully decoded token payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        logger.warning(f"JWT Error during token validation: {str(e)}")
        logger.warning(f"Token verification failed with SECRET_KEY: {settings.SECRET_KEY[:10]}... and ALGORITHM: {settings.ALGORITHM}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )