from redis.exceptions import RedisError
from app.core.redis import redis_client
import secrets
from redis.asyncio import Redis

_RELEASE_LOCK_SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
end
return 0
"""


async def acquire_cache_lock(
    redis: Redis, key: str, ttl_seconds: int = 10
) -> str | None:
    lock_token = secrets.token_urlsafe(16)
    acquired = await redis.set(key, lock_token, nx=True, ex=ttl_seconds)
    return lock_token if acquired else None


async def release_cache_lock(redis: Redis, key: str, lock_token: str) -> None:
    await redis.eval(_RELEASE_LOCK_SCRIPT, 1, key, lock_token)


async def get_cache_version(user_id: int) -> str | None:
    try:
        version = await redis_client.get(f"projects:version:user:{user_id}")
        return version or "0"

    except RedisError:
        return None


async def invalidate_project_list(user_id: int) -> None:
    await redis_client.incr(f"projects:version:user:{user_id}")