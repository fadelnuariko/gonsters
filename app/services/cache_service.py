import json
from app.database import get_redis_client
from app.utils.logger import logger

class CacheService:
    """Service for caching operations using Redis"""

    def __init__(self):
        self.redis_client = None
        self.default_ttl = 300  # 5 minutes default TTL

    def _get_client(self):
        """Get Redis client with connection retry"""
        if not self.redis_client:
            try:
                self.redis_client = get_redis_client()
                logger.debug("Redis client initialized")
            except Exception as e:
                logger.warning(f"Temporary Redis connection loss, self-healing retry is initiated", extra={
                    'extra_data': {'error': str(e)}
                })
                raise
        return self.redis_client

    def get(self, key: str):
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            client = self._get_client()
            value = client.get(key)

            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)

            logger.debug(f"Cache MISS: {key}")
            return None

        except Exception as e:
            logger.warning(f"Cache GET error for key '{key}': {e}")
            return None

    def set(self, key: str, value, ttl: int = None):
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 300)

        Returns:
            True if successful, False otherwise
        """
        try:
            client = self._get_client()
            ttl = ttl or self.default_ttl

            serialized_value = json.dumps(value)
            client.setex(key, ttl, serialized_value)

            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.warning(f"Cache SET error for key '{key}': {e}")
            return False

    def delete(self, key: str):
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            client = self._get_client()
            client.delete(key)

            logger.debug(f"Cache DELETE: {key}")
            return True

        except Exception as e:
            logger.warning(f"Cache DELETE error for key '{key}': {e}")
            return False

    def delete_pattern(self, pattern: str):
        """
        Delete all keys matching pattern

        Args:
            pattern: Pattern to match (e.g., 'machine:*')

        Returns:
            Number of keys deleted
        """
        try:
            client = self._get_client()
            keys = client.keys(pattern)

            if keys:
                deleted = client.delete(*keys)
                logger.debug(f"Cache DELETE pattern '{pattern}': {deleted} keys")
                return deleted

            return 0

        except Exception as e:
            logger.warning(f"Cache DELETE pattern error for '{pattern}': {e}")
            return 0

    def invalidate_machine_cache(self, machine_id: int = None):
        """
        Invalidate machine-related cache

        Args:
            machine_id: Specific machine ID to invalidate, or None for all
        """
        if machine_id:
            self.delete(f"machine:{machine_id}")
        else:
            self.delete_pattern("machine:*")
            self.delete("machines:all")

cache_service = CacheService()
