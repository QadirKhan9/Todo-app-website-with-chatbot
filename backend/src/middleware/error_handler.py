from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback
from typing import Callable


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle errors globally and log them appropriately
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # Log HTTP exceptions
            self.logger.warning(f"HTTPException: {e.status_code} - {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            # Log unexpected errors
            self.logger.error(f"Unexpected error: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Return a generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "message": "An unexpected error occurred. Please try again later."
                }
            )