from redis.exceptions import RedisError
from app.core.redis import redis_client

async def get_cache_version(user_id: int)-> str | None:
    try:
        version = await redis_client.get(
            f"projects:version:user:{user_id}"
        )
        return version or "0"
    
    except RedisError:
        return None
    
async def invalidate_project_list(user_id: int) -> None:
    await redis_client.incr(f"projects:version:user:{user_id}")