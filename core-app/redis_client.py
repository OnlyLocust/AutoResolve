import redis.asyncio as redis

redis_pool = None

async def init_redis():
    global redis_pool
    redis_pool = redis.ConnectionPool.from_url("redis://localhost:6380", decode_responses=True)

async def close_redis():
    if redis_pool:
        await redis_pool.disconnect()

def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)