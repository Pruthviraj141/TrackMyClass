import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException
from backend.core.redis_client import RedisManager

logger = logging.getLogger(__name__)

LIMITS = {
    "/api/v1/auth/login": (5, 60), # 5 requests per 60 seconds
    "/api/v1/registration/register": (10, 60),
    "/api/v1/attendance/mark-attendance": (100, 60)
}

# Fallback in-memory limiter for gracefully handling Redis crashes
_fallback_buckets = defaultdict(list)

# A standard Sliding Window Log algorithm executed safely inside Redis Lua
# to prevent race conditions during heavy API bombardment across nodes.
SLIDING_WINDOW_LUA = """
local key = KEYS[1]
local max_requests = tonumber(ARGV[1])
local window_secs = tonumber(ARGV[2])
local current_time = tonumber(ARGV[3])

-- Drop values outside the window
redis.call('ZREMRANGEBYSCORE', key, '-inf', current_time - window_secs)

-- Count what's left
local current_requests = redis.call('ZCARD', key)

if current_requests >= max_requests then
    return 0 -- Deny
else
    -- Add the new timestamp with score=time, value=time (must be distinct, so append random or micros)
    local member = current_time .. ':' .. math.random()
    redis.call('ZADD', key, current_time, member)
    redis.call('EXPIRE', key, window_secs + 1)
    return 1 -- Allow
end
"""

async def apply_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    
    limit_conf = LIMITS.get(path)
    if not limit_conf:
        return
        
    max_requests, window_secs = limit_conf
    key = f"ratelimit:{client_ip}:{path}"
    current_time = time.time()
    
    redis = RedisManager.get_client()
    
    if redis:
        try:
            # Distributed rate limit check
            allowed = await redis.eval(
                SLIDING_WINDOW_LUA, 
                1, 
                key, 
                max_requests, 
                window_secs, 
                current_time
            )
            if not allowed:
                raise HTTPException(status_code=429, detail="Too Many Requests")
            return
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Redis rate limiting failed ({e}), falling back to local Memory.")
            pass # Fallthrough to local bucket

    # Fallback to Local Limiting
    # (used if Redis is offline entirely, keeping the application alive!)
    local_key = f"{client_ip}:{path}"
    _fallback_buckets[local_key] = [t for t in _fallback_buckets[local_key] if current_time - t < window_secs]
    
    if len(_fallback_buckets[local_key]) >= max_requests:
        raise HTTPException(status_code=429, detail="Too Many Requests")
        
    _fallback_buckets[local_key].append(current_time)
