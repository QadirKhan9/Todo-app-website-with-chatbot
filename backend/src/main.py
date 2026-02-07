import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import api_router
from .config.settings import get_settings
from .db.session import create_db_and_tables
from .utils.logging import setup_logging


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    # Load settings
    settings = get_settings()

    # Set up logging
    setup_logging(
        log_level="WARNING",  # Changed to WARNING to capture important info without flooding with DEBUG/INFO
        log_file="logs/app.log"
    )

    # Reduce logging for SQLAlchemy engine to minimize noise
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.orm').setLevel(logging.ERROR)

    # Reduce logging for uvicorn access logs to minimize OPTIONS request noise
    class OptionsFilter(logging.Filter):
        def filter(self, record):
            # Filter out OPTIONS requests which are just CORS preflight requests
            if '"OPTIONS ' in record.getMessage():
                return False
            return True

    logging.getLogger("uvicorn.access").addFilter(OptionsFilter())
    
    # Create the FastAPI app
    app = FastAPI(
        title="Chat API & Orchestration Layer",
        description="A thin, stateless HTTP layer that connects the frontend UI with the AI Agent and MCP tools",
        version="0.0.1",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router)

    @app.get("/")
    def root():
        return {"status": "Backend is running"}

    
    # Create database tables on startup
    @app.on_event("startup")
    def on_startup():
        try:
            create_db_and_tables()
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Don't exit here, let FastAPI try to start anyway
    
    # Health check endpoint
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "chat-api-orchestration"}
    
    return app


# Create the main application instance
app = create_app()


# For running with uvicorn: uvicorn backend.src.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)