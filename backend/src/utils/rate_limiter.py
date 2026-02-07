from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI


def create_limiter(app: FastAPI):
    """
    Create and configure rate limiter for the application
    """
    # Initialize the limiter with a default limit
    limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per day"])
    
    # Add the rate limit exceeded handler to the app
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    return limiter