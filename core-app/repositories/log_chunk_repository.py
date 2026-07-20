from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from models.log_chunk import LogChunk


async def create_log_chunk(session: AsyncSession, chunk: LogChunk) -> LogChunk:
    session.add(chunk)
    # Commit the chunk to the database
    await session.commit()
    await session.refresh(chunk)
    return chunk


async def get_chunks_by_build_id(
    session: AsyncSession, build_id: str
) -> List[LogChunk]:
    result = await session.execute(
        select(LogChunk)
        .where(LogChunk.build_id == build_id)
        .order_by(LogChunk.chunk_index)
    )
    return list(result.scalars().all())


async def update_chunk_embedding(
    session: AsyncSession, chunk_id: str, embedding: List[float]
) -> None:
    chunk = await session.get(LogChunk, chunk_id)
    if chunk:
        chunk.embedding = embedding
        await session.flush()


async def search_similar_chunks(
    session: AsyncSession,
    build_id: str,
    query_embedding: List[float],
    limit: int = 3,
) -> List[dict]:
    """pgvector cosine similarity — only usable after Day 5 embeddings."""
    query = text("""
        SELECT content,
               1 - (embedding <=> CAST(:emb AS vector)) AS similarity
        FROM   log_chunks
        WHERE  build_id = :build_id
          AND  embedding IS NOT NULL
        ORDER  BY similarity DESC
        LIMIT  :limit
    """)
    result = await session.execute(
        query,
        {"emb": str(query_embedding), "build_id": build_id, "limit": limit},
    )
    return [{"content": r.content, "similarity": r.similarity}
            for r in result]