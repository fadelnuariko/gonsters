import pytest
from unittest.mock import Mock, patch
from app.services.cache_service import CacheService, cache_aside


class TestCacheService:
    """Test cases for CacheService"""

    @patch('app.services.cache_service.get_redis_client')
    def test_get_cache_hit(self, mock_redis):
        """Test cache hit scenario"""
        # Arrange
        mock_client = Mock()
        mock_client.get.return_value = '{"id": 1, "name": "Machine A"}'
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        
        # Act
        result = cache.get("machine:1")
        
        # Assert
        assert result == {"id": 1, "name": "Machine A"}
        mock_client.get.assert_called_once_with("machine:1")

    @patch('app.services.cache_service.get_redis_client')
    def test_get_cache_miss(self, mock_redis):
        """Test cache miss scenario"""
        # Arrange
        mock_client = Mock()
        mock_client.get.return_value = None
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        
        # Act
        result = cache.get("machine:999")
        
        # Assert
        assert result is None
        mock_client.get.assert_called_once_with("machine:999")

    @patch('app.services.cache_service.get_redis_client')
    def test_set_cache(self, mock_redis):
        """Test setting cache value"""
        # Arrange
        mock_client = Mock()
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        data = {"id": 1, "name": "Machine A"}
        
        # Act
        cache.set("machine:1", data, ttl=300)
        
        # Assert
        mock_client.setex.assert_called_once()
        args = mock_client.setex.call_args[0]
        assert args[0] == "machine:1"
        assert args[1] == 300

    @patch('app.services.cache_service.get_redis_client')
    def test_cache_aside_decorator(self, mock_redis):
        """Test cache-aside pattern decorator"""
        # Arrange
        mock_client = Mock()
        mock_client.get.return_value = None  # Cache miss
        mock_redis.return_value = mock_client
        
        call_count = 0
        
        @cache_aside(key_prefix="test", ttl=60)
        def expensive_function(arg):
            nonlocal call_count
            call_count += 1
            return {"result": arg}
        
        # Act
        result1 = expensive_function("value1")
        
        # Assert
        assert result1 == {"result": "value1"}
        assert call_count == 1
        mock_client.setex.assert_called_once()
