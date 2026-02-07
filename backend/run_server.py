from src.main import app
import uvicorn
import logging

# Configure root logger
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,  # Enable access logging to show HTTP requests
        log_config=None   # Use default uvicorn logging configuration
    )