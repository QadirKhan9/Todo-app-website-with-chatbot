from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.auth.jwt_handler import verify_token
from fastapi import Request


security = HTTPBearer()


async def jwt_bearer_scheme(credentials: HTTPAuthorizationCredentials):
    """Extract and validate JWT token from Authorization header"""
    token = credentials.credentials
    try:
        payload = verify_token(token)
        return payload
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token_payload: dict = security):
    """Get the current authenticated user from the token"""
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_payload


def require_authenticated_user(request: Request, token_payload: dict = security):
    """Middleware to ensure user is authenticated"""
    # Verify that the token is valid and return user info
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_payload


def verify_user_owns_resource(token_payload: dict, user_id_from_path: str):
    """Verify that the authenticated user owns the resource they're trying to access"""
    token_user_id = token_payload.get("user_id")
    if token_user_id != user_id_from_path:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )

    return token_payload