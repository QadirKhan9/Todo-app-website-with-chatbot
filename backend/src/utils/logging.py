import logging
from typing import Optional
from datetime import datetime
import json
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up logging configuration for the application.
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_conversation_event(
    conversation_id: str,
    user_id: str,
    event_type: str,
    details: dict = None,
    level: str = "INFO"
):
    """
    Log conversation-specific events.
    """
    logger = logging.getLogger("conversation")
    
    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "conversation_id": conversation_id,
        "user_id": user_id,
        "event_type": event_type,
        "details": details or {}
    }
    
    log_func = getattr(logger, level.lower())
    log_func(json.dumps(event_data))


def log_ai_interaction(
    conversation_id: str,
    user_id: str,
    input_text: str,
    output_text: str,
    model_used: str,
    duration_ms: float
):
    """
    Log AI interaction details for monitoring and analysis.
    """
    logger = logging.getLogger("ai_interaction")
    
    interaction_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "conversation_id": conversation_id,
        "user_id": user_id,
        "input": input_text,
        "output": output_text,
        "model": model_used,
        "duration_ms": duration_ms
    }
    
    logger.info(json.dumps(interaction_data))