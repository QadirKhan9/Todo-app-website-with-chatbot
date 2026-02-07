import logging
from fastapi import HTTPException, status
from typing import Dict, Any
import json


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatAPIException(HTTPException):
    """
    Custom exception class for Chat API specific errors.
    """
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)
        logger.error(f"ChatAPIException: {detail} (Status: {status_code})")


class ValidationError(ChatAPIException):
    """
    Exception raised for validation errors.
    """
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AuthenticationError(ChatAPIException):
    """
    Exception raised for authentication errors.
    """
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(ChatAPIException):
    """
    Exception raised for authorization errors.
    """
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ResourceNotFoundError(ChatAPIException):
    """
    Exception raised when a requested resource is not found.
    """
    def __init__(self, resource_type: str, resource_id: str):
        detail = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


def log_api_call(endpoint: str, user_id: str, request_data: Dict[str, Any]):
    """
    Log API calls for monitoring and debugging.
    """
    logger.info(f"API Call: {endpoint}, User: {user_id}, Data: {json.dumps(request_data)}")


def log_error(error: Exception, context: str = ""):
    """
    Log errors with context for debugging.
    """
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)