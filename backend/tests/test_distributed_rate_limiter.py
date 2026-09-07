import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from backend.api.rate_limiting import TokenBucketRateLimiter
from backend.core.errors import RateLimitExceeded

@pytest.mark.asyncio
async def test_fallback_local_rate_limiting():
    # If redis fails or is not connected, it falls back to Memory mode smoothly
    limiter = TokenBucketRateLimiter(namespace="test_local", quota=2, window=10)
    
    # Send 2 OK
    with patch("backend.core.redis_client.RedisManager.get_client", return_value=None):
        await limiter.acquire("user_1")
        await limiter.acquire("user_1")
        
        # 3rd should fail
        with pytest.raises(RateLimitExceeded):
            await limiter.acquire("user_1")


@pytest.mark.asyncio
async def test_distributed_redis_rate_limiting():
    limiter = TokenBucketRateLimiter(namespace="test_dist", quota=3, window=10)
    
    mock_redis = AsyncMock()
    # First 3 hits return (1, 1, 1), 4th returns (0)
    mock_redis.evalsha.side_effect = [1, 1, 1, 0]
    
    with patch("backend.core.redis_client.RedisManager.get_client", return_value=mock_redis):
        # 3 OK
        await limiter.acquire("user_2")
        await limiter.acquire("user_2")
        await limiter.acquire("user_2")
        
        # 4th fails
        with pytest.raises(RateLimitExceeded):
            await limiter.acquire("user_2")
            
        assert mock_redis.evalsha.call_count == 4
