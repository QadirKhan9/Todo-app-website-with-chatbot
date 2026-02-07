import logging
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.auth_service import AuthService
from ..core.security import verify_token
from ..models.user_model import User
from ..schemas.auth import TokenData


# Configure logging
logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_current_user_token_data(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> TokenData:
    """
    Dependency to get the current authenticated user token data
    """
    token = credentials.credentials

    # Log the token for debugging (be careful with production logs)
    logger.debug(f"Received token for validation: {token[:20] if token else 'None'}...")

    try:
        payload = verify_token(token)

        # Log payload for debugging
        logger.debug(f"Decoded token payload: {payload}")

        user_id = payload.get("sub")
        email = payload.get("email")
        token_type = payload.get("type")

        # Validate that user_id is a string and not a dict or other type
        if not isinstance(user_id, str) or not user_id:
            logger.warning(f"Invalid user_id in token: {user_id} (type: {type(user_id)})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - invalid user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not isinstance(email, str) or not email:
            logger.warning(f"Invalid email in token: {email} (type: {type(email)})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - invalid email",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token_type != "access":
            logger.warning(f"Invalid token type: {token_type}, expected: access")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate that the user_id is a proper UUID string
        try:
            uuid.UUID(user_id)  # This will raise ValueError if invalid
        except ValueError:
            logger.warning(f"Invalid UUID format in token: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - invalid user ID format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = TokenData(user_id=user_id, email=email, token_type=token_type)
        logger.info(f"Successfully authenticated user: {user_id}")
        return token_data
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user object
    """
    token = credentials.credentials

    # Log the token for debugging (be careful with production logs)
    logger.debug(f"Received token for validation: {token[:20] if token else 'None'}...")

    try:
        payload = verify_token(token)

        # Log payload for debugging
        logger.debug(f"Decoded token payload: {payload}")

        user_id = payload.get("sub")
        email = payload.get("email")
        token_type = payload.get("type")

        # Validate that user_id is a string and not a dict or other type
        if not isinstance(user_id, str) or not user_id:
            logger.warning(f"Invalid user_id in token: {user_id} (type: {type(user_id)})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - invalid user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not isinstance(email, str) or not email:
            logger.warning(f"Invalid email in token: {email} (type: {type(email)})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - invalid email",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token_type != "access":
            logger.warning(f"Invalid token type: {token_type}, expected: access")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get the user from the database
        # Convert user_id to UUID format to match the database schema
        try:
            user_uuid = uuid.UUID(user_id)
            user = db.query(User).filter(User.id == user_uuid).first()
        except ValueError:
            logger.warning(f"Invalid UUID format in token: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - invalid user ID format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user:
            logger.warning(f"User not found in database: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"Successfully authenticated user: {user_id}")
        return user
    except HTTPException as e:
        # Log HTTP exceptions for debugging
        logger.warning(f"HTTPException during token validation: {e.detail}")
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """
    Dependency to get the authentication service
    """
    return AuthService(db=db)