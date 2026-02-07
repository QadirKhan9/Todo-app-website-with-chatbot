from fastapi import HTTPException, status, Request
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from .config import settings
from ..models.user_model import User
import uuid


class AuthMiddleware:
    def __init__(self):
        self.security = HTTPBearer()
    
    async def verify_token(self, request: Request):
        """
        Verify the JWT token in the request
        """
        try:
            # Extract token from request
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or missing token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Remove 'Bearer ' prefix
            token = token[7:]
            
            # Decode and verify the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # In a real implementation, you would fetch the user from the database
            # For now, returning a mock user
            user = User(id=uuid.uuid4(), email="mock@example.com")
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Add user to request state
            request.state.user = user
            return user
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Create an instance of the middleware
auth_middleware = AuthMiddleware()