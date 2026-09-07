import logging
from typing import Optional
from redis import asyncio as aioredis
from backend.core.config import REDIS_URL

logger = logging.getLogger(__name__)

class RedisManager:
    _instance: Optional[aioredis.Redis] = None
    _enabled: bool = True  # Track if Redis failed completely

    @classmethod
    async def init(cls) -> None:
        """Initialize the Redis connection pool."""
        try:
            cls._instance = aioredis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0,       # 2 sec timeout so APIs don't hang if Redis dies
                socket_connect_timeout=2.0
            )
            # Ping to verify
            await cls._instance.ping()
            logger.info("✅ Redis connected successfully.")
            cls._enabled = True
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Degrading gracefully to local limits.")
            cls._enabled = False

    @classmethod
    async def close(cls) -> None:
        """Close the Redis pool."""
        if cls._instance:
            await cls._instance.close()
            logger.info("🛑 Redis connection closed.")

    @classmethod
    def get_client(cls) -> Optional[aioredis.Redis]:
        """Get the active Redis client. Returns None if disabled/failed."""
        if cls._enabled:
            return cls._instance
        return None

async def init_redis():
    await RedisManager.init()

async def close_redis():
    await RedisManager.close()
