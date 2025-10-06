"""
Rate limiting utility using Redis
"""
import redis
import time
import asyncio
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Redis client
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Rate limiting will be disabled.")
    redis_client = None

async def rate_limit(
    identifier: str,
    limit: int = 100,
    window: int = 60
) -> bool:
    """
    Rate limiting using sliding window counter
    
    Args:
        identifier: Unique identifier (IP, user ID, etc.)
        limit: Maximum requests allowed in window
        window: Time window in seconds
    
    Returns:
        True if request is allowed, False if rate limited
    """
    if not redis_client:
        # If Redis is unavailable, allow all requests
        return True
    
    try:
        key = f"rate_limit:{identifier}"
        current_time = int(time.time())
        
        # Use Redis pipeline for atomic operations
        pipe = redis_client.pipeline()
        
        # Remove expired entries
        pipe.zremrangebyscore(key, 0, current_time - window)
        
        # Count current requests in window
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipe.expire(key, window)
        
        results = pipe.execute()
        
        # Check if under limit (before adding current request)
        current_count = results[1]
        
        if current_count >= limit:
            # Remove the request we just added since it's rate limited
            redis_client.zrem(key, str(current_time))
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Rate limiting error: {e}")
        # If there's an error, allow the request
        return True

async def get_rate_limit_status(identifier: str, window: int = 60) -> dict:
    """
    Get current rate limit status for an identifier
    """
    if not redis_client:
        return {"requests": 0, "limit": settings.RATE_LIMIT_REQUESTS, "window": window}
    
    try:
        key = f"rate_limit:{identifier}"
        current_time = int(time.time())
        
        # Clean up expired entries and count current requests
        redis_client.zremrangebyscore(key, 0, current_time - window)
        current_count = redis_client.zcard(key)
        
        return {
            "requests": current_count,
            "limit": settings.RATE_LIMIT_REQUESTS,
            "window": window,
            "remaining": max(0, settings.RATE_LIMIT_REQUESTS - current_count)
        }
        
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        return {"requests": 0, "limit": settings.RATE_LIMIT_REQUESTS, "window": window}

def reset_rate_limit(identifier: str):
    """Reset rate limit for an identifier"""
    if redis_client:
        try:
            key = f"rate_limit:{identifier}"
            redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error resetting rate limit: {e}")