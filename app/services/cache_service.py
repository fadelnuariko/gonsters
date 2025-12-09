import json
import time
from functools import wraps
from app.database import get_redis_client
from app.utils.logger import logger


class CacheService:
    """Redis caching service with Cache-Aside Pattern"""

    def __init__(self):
        self.redis_client = None
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def _get_client(self):
        """Get Redis client with retry logic"""
        if self.redis_client is None:
            for attempt in range(1, self.max_retries + 1):
                try:
                    self.redis_client = get_redis_client()
                    logger.info("Redis connection established")
                    return self.redis_client
                except Exception as e:
                    logger.warning(
                        f"Temporary Redis connection loss, self-healing retry is initiated (attempt {attempt}/{self.max_retries})",
                        extra={
                            "extra_data": {
                                "attempt": attempt,
                                "max_retries": self.max_retries,
                                "error": str(e),
                            }
                        },
                    )
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)
                    else:
                        logger.error(
                            f"Failed to connect to Redis after {self.max_retries} attempts",
                            extra={"extra_data": {"error": str(e)}},
                        )
                        raise
        return self.redis_client

    def get(self, key: str):
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value (deserialized from JSON) or None if not found
        """
        try:
            client = self._get_client()
            value = client.get(key)

            if value:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(value)

            logger.debug(f"Cache miss for key: {key}")
            return None

        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    def set(self, key: str, value, ttl: int = 300):
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache (will be serialized to JSON)
            ttl: Time to live in seconds (default: 5 minutes)
        """
        try:
            client = self._get_client()
            serialized_value = json.dumps(value)
            client.setex(key, ttl, serialized_value)

            logger.debug(f"Cache set for key: {key} with TTL: {ttl}s")

        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")

    def delete(self, key: str):
        """Delete key from cache"""
        try:
            client = self._get_client()
            client.delete(key)
            logger.debug(f"Cache deleted for key: {key}")

        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")

    def invalidate_pattern(self, pattern: str):
        """
        Invalidate all keys matching pattern

        Args:
            pattern: Redis key pattern (e.g., "machine:*")
        """
        try:
            client = self._get_client()
            keys = client.keys(pattern)

            if keys:
                client.delete(*keys)
                logger.info(
                    f"Invalidated {len(keys)} cache keys matching pattern: {pattern}"
                )

        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")


def cache_aside(key_prefix: str, ttl: int = 300):
    """
    Decorator implementing Cache-Aside Pattern

    Usage:
        @cache_aside(key_prefix="machine", ttl=600)
        def get_machine_by_id(machine_id):
            # Database query here
            return machine_data

    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = CacheService()

            # Generate cache key from function arguments
            cache_key = f"{key_prefix}:{':'.join(map(str, args))}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Returning cached value for {func.__name__}")
                return cached_value

            # Cache miss - execute function
            logger.debug(f"Cache miss - executing {func.__name__}")
            result = func(*args, **kwargs)

            # Store in cache
            if result is not None:
                cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


# Singleton instance
cache_service = CacheService()
