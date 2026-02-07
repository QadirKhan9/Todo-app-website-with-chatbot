"""
Performance optimization for Chat API & Orchestration Layer
This module implements performance optimizations for the chat API endpoints
"""

import asyncio
import time
from typing import Dict, Any, Optional
from functools import wraps
import logging

from ..models.message import Message
from ..services.conversation_service import ConversationService
from ..services.ai_agent_service import AIAgentService


def performance_monitor(func):
    """Decorator to monitor the performance of functions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            duration = end_time - start_time
            logging.info(f"{func.__name__} took {duration:.4f} seconds")
            
            # Log slow requests
            if duration > 1.0:  # Log if taking more than 1 second
                logging.warning(f"SLOW REQUEST: {func.__name__} took {duration:.4f} seconds")
    return wrapper


class OptimizedAIAgentService(AIAgentService):
    """
    Optimized version of AIAgentService with performance enhancements
    """
    
    def __init__(self):
        super().__init__()
        self._conversation_cache = {}  # Simple cache for conversation history
        self.cache_ttl = 300  # 5 minutes TTL for cache entries

    @performance_monitor
    async def load_conversation_history(self, conversation_id: str) -> list:
        """
        Load the conversation history for the AI agent context with caching.
        """
        # Check cache first
        cache_key = f"conv_hist_{conversation_id}"
        if cache_key in self._conversation_cache:
            cached_data, timestamp = self._conversation_cache[cache_key]
            # Check if cache is still valid
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        # Load from service
        from .conversation_service import ConversationService
        service = ConversationService()
        messages = await service.get_messages(conversation_id)

        # Convert to the format expected by Google Gemini
        # Gemini expects a list of dicts with role and parts
        formatted_messages = []
        for msg in messages:
            # Map our internal role to Gemini's expected format
            if msg.role.value.lower() == "user":
                role = "user"
            elif msg.role.value.lower() == "assistant":
                role = "model"  # In Gemini, the model represents the AI assistant
            else:
                role = "user"  # Default for other roles

            formatted_messages.append({
                "role": role,
                "content": msg.content,
                "parts": [msg.content]  # Gemini expects content in a parts array
            })

        # Cache the result
        self._conversation_cache[cache_key] = (formatted_messages, time.time())
        
        return formatted_messages


class OptimizedConversationService(ConversationService):
    """
    Optimized version of ConversationService with performance enhancements
    """
    
    def __init__(self):
        super().__init__()
        self._message_cache = {}  # Cache for messages
        self._conversation_cache = {}  # Cache for conversations
        self.cache_ttl = 300  # 5 minutes TTL for cache entries

    @performance_monitor
    async def get_messages(self, conversation_id: str) -> list:
        """
        Get messages for a conversation with caching.
        """
        # Check cache first
        cache_key = f"msgs_{conversation_id}"
        if cache_key in self._message_cache:
            cached_data, timestamp = self._message_cache[cache_key]
            # Check if cache is still valid
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        # Load from DB
        messages = await super().get_messages(conversation_id)
        
        # Cache the result
        self._message_cache[cache_key] = (messages, time.time())
        
        return messages

    @performance_monitor
    async def get_conversation(self, conversation_id: str) -> Optional[Any]:
        """
        Get a conversation with caching.
        """
        # Check cache first
        cache_key = f"conv_{conversation_id}"
        if cache_key in self._conversation_cache:
            cached_data, timestamp = self._conversation_cache[cache_key]
            # Check if cache is still valid
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        # Load from DB
        conversation = await super().get_conversation(conversation_id)
        
        # Cache the result
        self._conversation_cache[cache_key] = (conversation, time.time())
        
        return conversation


def bulk_insert_messages(messages: list) -> None:
    """
    Bulk insert multiple messages for better performance when processing
    multiple messages in a conversation.
    """
    # Implementation would depend on the specific database ORM being used
    # This is a placeholder for the concept
    pass


def optimize_database_queries():
    """
    Apply database query optimizations such as:
    - Adding proper indexes
    - Using connection pooling
    - Implementing query batching where appropriate
    """
    # This would typically involve:
    # 1. Ensuring proper indexes on frequently queried columns
    # 2. Setting up connection pooling
    # 3. Using eager loading where appropriate to prevent N+1 queries
    pass


async def process_concurrent_messages(conversation_id: str, messages: list) -> list:
    """
    Process multiple messages concurrently for better performance.
    """
    async def process_single_message(msg_data):
        ai_service = AIAgentService()  # Use regular service or optimized one
        return await ai_service.process_message_with_tools(
            conversation_id=conversation_id,
            user_message=msg_data
        )
    
    # Process all messages concurrently
    tasks = [process_single_message(msg) for msg in messages]
    results = await asyncio.gather(*tasks)
    
    return results