import logging
import traceback
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Union, Optional
from pydantic import BaseModel
from ..database import get_db
from ..schemas.auth import (
    UserCreate, UserLogin, Token, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest, UserResponse
)
from ..services.auth_service import AuthService
from ..core.security import (
    create_access_token, create_refresh_token, verify_token,
    verify_password, get_password_hash
)
from ..dependencies.auth import get_current_user, get_auth_service
from ..models.user_model import User

# Configure logging
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


from fastapi.responses import JSONResponse

# Define a custom response model for user data
class UserData(BaseModel):
    id: str
    email: str
    username: Optional[str] = None

# Define a custom response model for login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserData


@router.post("/signup", response_model=LoginResponse)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user with email and password and return access token
    """
    try:
        logger.info(f"Signup attempt for email: {user_data.email}")
        user = auth_service.register_user(user_data)
        logger.info(f"User registered successfully: {user.id}")

        # Create access token for the newly registered user
        access_token_expires = timedelta(minutes=30)  # configurable
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )

        logger.info(f"Access token created for new user: {user.id}")

        # Ensure token is not None
        if not access_token:
            logger.error("Failed to generate access token for new user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate access token"
            )

        # Return success response with token and user data
        logger.info(f"Returning signup response for user: {user.id}")
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserData(
                id=str(user.id),  # Convert UUID to string
                email=user.email,
                username=user.username
            )
        )
    except HTTPException as e:
        # Log HTTP exceptions as warnings (especially 409 conflicts)
        logger.warning(f"Auth warning: {e.detail}")

        # Re-raise HTTP exceptions as-is, preserving the original status code and message
        # The AuthService already handles the specific error messages appropriately
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error during signup: {str(e)}")
        logger.exception("Full traceback for signup error:")  # Log the full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later."
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return access token with user info
    """
    try:
        logger.info(f"Login attempt for email: {user_credentials.email}")

        # Log the authentication attempt
        user = auth_service.authenticate_user(user_credentials)
        logger.info(f"User authenticated successfully: {user.id}")

        # Create access token
        access_token_expires = timedelta(minutes=30)  # configurable
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )

        logger.info(f"Access token created for user: {user.id}")

        # Ensure token is not None
        if not access_token:
            logger.error("Failed to generate access token")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate access token"
            )

        logger.info(f"Returning login response for user: {user.id}")
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserData(
                id=str(user.id),  # Convert UUID to string
                email=user.email,
                username=user.username
            )
        )
    except HTTPException as e:
        # Log HTTP exceptions as warnings with more details
        logger.warning(f"Auth warning during login for email {user_credentials.email}: {e.detail}")
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login for email {user_credentials.email}: {str(e)}")
        logger.exception("Full traceback for login error:")  # Log the full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication"
        )


@router.post("/signin", response_model=LoginResponse)
async def signin(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return access token with user info (alias for login)
    """
    # Call the same login function to avoid duplicating logic
    return await login(user_credentials, db, auth_service)


@router.post("/logout")
async def logout():
    """
    Logout user (client-side token removal is sufficient)
    """
    return {"message": "Successfully logged out"}


# Define a response model for the /me endpoint
class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile
    """
    # The current_user is already the user object from the dependency
    # No need to query the database again
    return UserProfileResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at
    )


@router.post("/refresh", response_model=Dict[str, str])
async def refresh_access_token(
    refresh_request: RefreshTokenRequest
):
    """
    Refresh access token using refresh token
    """
    try:
        payload = verify_token(refresh_request.refresh_token)

        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new access token
        access_token = create_access_token(data={"sub": user_id, "email": email})

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        # Log HTTP exceptions as warnings
        logger.warning(f"Auth warning during token refresh: {e.detail}")
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during token refresh"
        )


@router.post("/verify-email")
async def verify_email(
    verification_data: VerifyEmailRequest
):
    """
    Verify user email using token (placeholder implementation)
    """
    try:
        # In a real implementation, you would:
        # 1. Verify the token
        # 2. Find the associated user
        # 3. Update email_verified field to True
        # 4. Return success response

        # Placeholder implementation
        payload = verify_token(verification_data.token)

        if payload.get("type") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type for email verification"
            )

        # Here you would typically update the user's email_verified status
        # For now, we'll just return a success message
        return {"message": "Email verified successfully"}
    except HTTPException as e:
        # Log HTTP exceptions as warnings
        logger.warning(f"Auth warning during email verification: {e.detail}")
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during email verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during email verification"
        )


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Initiate password reset process (placeholder implementation)
    """
    # In a real implementation, you would:
    # 1. Check if user exists
    # 2. Generate a password reset token
    # 3. Send email with reset link containing the token
    # 4. Store the token in database with expiration
    
    # Placeholder implementation
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # To prevent user enumeration, return success even if user doesn't exist
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Here you would generate a password reset token and send it via email
    # For now, we'll just return a success message
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset user password using reset token (placeholder implementation)
    """
    try:
        # In a real implementation, you would:
        # 1. Verify the reset token
        # 2. Validate the new password
        # 3. Hash the new password
        # 4. Update the user's password
        # 5. Invalidate all active sessions for the user

        # Placeholder implementation
        payload = verify_token(reset_data.token)

        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type for password reset"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )

        # Find the user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Hash the new password
        hashed_password = get_password_hash(reset_data.new_password)

        # Update the user's password
        user.hashed_password = hashed_password
        db.commit()

        return {"message": "Password reset successfully"}
    except HTTPException as e:
        # Log HTTP exceptions as warnings
        logger.warning(f"Auth warning during password reset: {e.detail}")
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during password reset"
        )