import os
from django.core.cache import caches
from django.conf import settings
from django.utils.decorators import method_decorator
from functools import wraps

# ===========================
# 1. Cache Configuration
# ===========================

# Default cache instance (Redis)
default_cache = caches['default']

# Cache timeout settings (in seconds)
CACHE_TIMEOUTS = {
    'short': 300,  # 5 minutes
    'medium': 1800,  # 30 minutes
    'long': 3600,  # 1 hour
}

# ===========================
# 2. Cache Key Management
# ===========================

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a unique cache key based on a prefix and arguments.
    Example: generate_cache_key('predictions', user_id=1, sector='tech')
    Output: 'predictions:user_id=1:sector=tech'
    """
    key_parts = [prefix]
    key_parts.extend([f"{k}={v}" for k, v in kwargs.items()])
    return ":".join(key_parts)

# ===========================
# 3. Cache Utilities
# ===========================

def get_from_cache(key: str):
    """
    Retrieve data from the cache using the given key.
    Returns None if the key does not exist.
    """
    return default_cache.get(key)

def set_to_cache(key: str, value, timeout: int = None):
    """
    Store data in the cache with an optional timeout.
    If no timeout is provided, the default medium timeout is used.
    """
    timeout = timeout or CACHE_TIMEOUTS['medium']
    default_cache.set(key, value, timeout)

def delete_from_cache(key: str):
    """
    Delete a specific key from the cache.
    """
    default_cache.delete(key)

def clear_cache():
    """
    Clear all keys from the cache.
    Use with caution in production environments.
    """
    default_cache.clear()

# ===========================
# 4. Cache Decorators
# ===========================

def cache_result(key_prefix: str, timeout: int = None):
    """
    Decorator to cache the result of a function.
    The cache key is generated dynamically based on the function name and arguments.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique cache key
            cache_key = generate_cache_key(key_prefix, *args, **kwargs)

            # Try to retrieve the result from the cache
            cached_result = get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

            # Call the function and cache the result
            result = func(*args, **kwargs)
            set_to_cache(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

# ===========================
# 5. Class-Based Cache Decorator
# ===========================

def class_cache_result(key_prefix: str, timeout: int = None):
    """
    Decorator to cache the result of a class method.
    The cache key is generated dynamically based on the class name, method name, and arguments.
    """
    def decorator(method):
        @wraps(method)
        def wrapper(instance, *args, **kwargs):
            # Generate a unique cache key
            cache_key = generate_cache_key(
                key_prefix,
                class_name=instance.__class__.__name__,
                method_name=method.__name__,
                *args,
                **kwargs
            )

            # Try to retrieve the result from the cache
            cached_result = get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

            # Call the method and cache the result
            result = method(instance, *args, **kwargs)
            set_to_cache(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

# ===========================
# 6. Cache Invalidation Utilities
# ===========================

def invalidate_cache_by_prefix(prefix: str):
    """
    Invalidate all cache keys that start with the given prefix.
    """
    for key in default_cache.keys(f"{prefix}:*"):
        delete_from_cache(key)

# ===========================
# 7. Logging & Monitoring
# ===========================

import logging

logger = logging.getLogger(__name__)

def log_cache_usage(action: str, key: str, result=None):
    """
    Log cache usage for monitoring and debugging.
    """
    logger.info(f"Cache {action}: {key}")
    if result is not None:
        logger.debug(f"Cache {action} result: {result}")

# ===========================
# 8. Example Usage
# ===========================

@cache_result(key_prefix="financial_data", timeout=CACHE_TIMEOUTS['medium'])
def fetch_financial_data(sector: str, country: str):
    """
    Example function to fetch financial data with caching.
    """
    # Simulate fetching data from an external API or database
    log_cache_usage("fetch", f"financial_data:sector={sector}:country={country}")
    return {
        "sector": sector,
        "country": country,
        "data": "Sample financial data"
    }
