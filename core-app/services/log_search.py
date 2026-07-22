from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from services.embedding_service import generate_embedding

async def search_relevant_logs(session: AsyncSession, build_id: str, query: str) -> list[dict]:
    """Finds the top 3 most semantically relevant log chunks for a given query."""
    
    print(f"🔍 Generating query embedding for: '{query}'")
    query_vec = await generate_embedding(query)
    
    # Format the vector safely as a string for raw SQL pgvector ingestion: '[0.1, 0.2, ...]'
    vector_str = f"[{','.join(map(str, query_vec))}]"
    
    # Use pgvector's cosine distance operator (<=>)
    sql = text("""
        SELECT chunk_index, content, 1 - (embedding <=> :query_vec) AS similarity
        FROM log_chunks
        WHERE build_id = :build_id
        ORDER BY embedding <=> :query_vec ASC
        LIMIT 3
    """)
    
    result = await session.execute(sql, {"build_id": build_id, "query_vec": vector_str})
    
    relevant_chunks = []
    for row in result:
        relevant_chunks.append({
            "chunk_index": row.chunk_index,
            "similarity": round(row.similarity, 4),
            "content": row.content
        })
        
    return relevant_chunks