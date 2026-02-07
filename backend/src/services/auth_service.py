import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import Optional
import traceback
from src.models.user_model import User
from src.schemas.auth import UserCreate, UserLogin, UserResponse
from src.core.security import verify_password, get_password_hash
import uuid


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user with email, username and password
        """
        # Normalize the email (strip whitespace and convert to lowercase)
        normalized_email = user_data.email.strip().lower()
        username = user_data.username.strip()

        # Check if user with this email already exists
        existing_user_by_email = self.db.query(User).filter(func.lower(User.email) == normalized_email).first()
        if existing_user_by_email:
            logger.warning(f"Attempted to create duplicate user with email: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Check if user with this username already exists
        existing_user_by_username = self.db.query(User).filter(func.lower(User.username) == username.lower()).first()
        if existing_user_by_username:
            logger.warning(f"Attempted to create duplicate user with username: {username}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists"
            )

        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create new user with normalized email and username
        db_user = User(
            email=normalized_email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            email_verified=False
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"Successfully created user with email: {normalized_email}")

            # Convert to UserResponse to ensure consistent return type
            return UserResponse(
                id=str(db_user.id),
                email=db_user.email,
                username=db_user.username,
                is_active=db_user.is_active,
                email_verified=db_user.email_verified,
                created_at=db_user.created_at
            )
        except IntegrityError as e:
            self.db.rollback()
            # Even though we checked for duplicates, there could be a race condition
            # where another request creates the same user between our check and insert
            # In this case, we'll still catch the IntegrityError but log it as a warning
            logger.warning(f"Attempted to create duplicate user with email: {normalized_email} or username: {username}")

            # Check if it's a unique violation (duplicate email or username)
            orig_error = getattr(e, 'orig', None)
            if orig_error:
                # Check for PostgreSQL unique violation
                pg_error_code = getattr(orig_error, 'pgcode', None)
                if pg_error_code == '23505':  # Unique violation code
                    # Check the error message to determine if it's email or username conflict
                    error_msg = str(e.orig)
                    if 'email' in error_msg.lower():
                        logger.warning(f"Duplicate email creation attempt (race condition) with email: {normalized_email}")
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="A user with this email already exists"
                        )
                    elif 'username' in error_msg.lower():
                        logger.warning(f"Duplicate username creation attempt (race condition) with username: {username}")
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="A user with this username already exists"
                        )

            # For any other integrity error, return a 500
            # Log the error without the full traceback for expected conflicts
            logger.error(f"IntegrityError during user creation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during user registration"
            )
        except Exception as e:
            self.db.rollback()
            # Log the error without the full traceback for cleaner logs
            logger.error(f"Unexpected error during user creation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during user registration"
            )

    def authenticate_user(self, user_login: UserLogin) -> User:
        """
        Authenticate user credentials and return user object if valid
        """
        # Normalize the email for lookup (strip whitespace and convert to lowercase)
        normalized_email = user_login.email.strip().lower()
        logger.info(f"Attempting to authenticate user with email: {normalized_email}")

        user = self.db.query(User).filter(func.lower(User.email) == normalized_email).first()

        if not user:
            logger.warning(f"Authentication failed: No user found with email: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Log whether the password verification passes
        password_valid = verify_password(user_login.password, user.hashed_password)
        logger.info(f"Password verification result for {normalized_email}: {password_valid}")

        if not password_valid:
            logger.warning(f"Authentication failed: Invalid password for email: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"Authentication failed: User account is deactivated for email: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"Successfully authenticated user: {user.id}")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email
        """
        # Normalize the email for lookup (strip whitespace and convert to lowercase)
        normalized_email = email.strip().lower()
        return self.db.query(User).filter(func.lower(User.email) == normalized_email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username
        """
        # Normalize the username for lookup (strip whitespace and convert to lowercase)
        normalized_username = username.strip().lower()
        return self.db.query(User).filter(func.lower(User.username) == normalized_username).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by ID
        """
        try:
            uuid_obj = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        return self.db.query(User).filter(User.id == uuid_obj).first()

    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account
        """
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False

    def activate_user(self, user_id: str) -> bool:
        """
        Activate a user account
        """
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = True
            self.db.commit()
            return True
        return False