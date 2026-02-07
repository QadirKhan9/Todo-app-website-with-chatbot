import redis
import json
import logging
from typing import Any, Optional
from ..config.settings import get_settings
settings = get_settings()


class CacheManager:
    """
    Manager for handling caching operations using Redis
    """
    
    def __init__(self):
        try:
            # Initialize Redis connection
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            
            # Test the connection
            self.redis_client.ping()
            self.enabled = True
            logging.info("Redis cache connected successfully")
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache
        """
        if not self.enabled:
            return None
            
        try:
            cached_value = self.redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
            return None
        except Exception as e:
            logging.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, expiration: int = 3600) -> bool:
        """
        Set a value in cache with optional expiration (in seconds)
        """
        if not self.enabled:
            return False
            
        try:
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, expiration, serialized_value)
            return True
        except Exception as e:
            logging.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache
        """
        if not self.enabled:
            return False
            
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logging.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        """
        if not self.enabled:
            return 0
            
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                return result
            return 0
        except Exception as e:
            logging.error(f"Cache invalidate pattern error for pattern {pattern}: {e}")
            return 0


# Global cache manager instance
cache_manager = CacheManager()


def get_cache_key(entity_type: str, entity_id: str, user_id: str = None) -> str:
    """
    Generate a standardized cache key
    """
    if user_id:
        return f"{entity_type}:{user_id}:{entity_id}"
    return f"{entity_type}:{entity_id}"


def get_user_cache_key(entity_type: str, user_id: str) -> str:
    """
    Generate a cache key for user-specific collections
    """
    return f"{entity_type}_list:{user_id}"