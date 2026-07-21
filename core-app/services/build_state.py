from redis_client import get_redis

TTL_SECONDS = 3600  # 1 hour expiration for cleanup

async def track_chunk_received(build_id: str, total_chunks: int) -> bool:
    r = get_redis()
    chunks_key = f"build:{build_id}:chunks_received"

    # Atomic increment prevents race conditions
    current_count = await r.incr(chunks_key)

    if current_count == 1:
        # First chunk establishes the state tracking
        await r.expire(chunks_key, TTL_SECONDS)
        await r.setex(f"build:{build_id}:total_chunks", TTL_SECONDS, str(total_chunks))
        await r.setex(f"build:{build_id}:status", TTL_SECONDS, "PROCESSING")

    if current_count == total_chunks:
        await r.set(f"build:{build_id}:status", "CLASSIFYING")
        return True

    return False