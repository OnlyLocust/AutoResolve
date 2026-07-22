import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from models.log_chunk import LogChunk
from repositories.log_chunk_repository import create_log_chunk
from repositories.build_repository import update_build_status
from schemas.kafka_message import KafkaMessage
from services.kafka_producer import send_log_chunk
from services.embedding_service import generate_embedding

async def chunk_and_save_logs(
    session: AsyncSession, 
    build_id: str, 
    repo_name: str, 
    extracted_logs: dict, 
    chunk_size: int = 500
):
    total_chunks_saved = 0
    global_chunk_index = 0  # Track the index continuously across all files
    
    # Calculate the absolute total of all chunks across all files first
    total_chunks_all_files = 0
    for log_text in extracted_logs.values():
        lines = log_text.splitlines()
        total_chunks_all_files += len([lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)])
    
    for file_name, log_text in extracted_logs.items():
        lines = log_text.splitlines()
        chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
        
        for chunk_lines in chunks:
            chunk_content = "\n".join(chunk_lines)
            chunk_full_content = f"--- File: {file_name} ---\n{chunk_content}"
            
            # --- DAY 5: Generate the vector ---
            print(f"🧠 Generating embedding for chunk {global_chunk_index}...")
            embedding_vec = await generate_embedding(chunk_full_content)
            
            await asyncio.sleep(10)

            # 1. Persist the log segment inside PostgreSQL for long-term historical records
            chunk_record = LogChunk(
                build_id=build_id,
                chunk_index=global_chunk_index,
                total_chunks=total_chunks_all_files,
                content=chunk_full_content,
                embedding=embedding_vec  # <-- Save the vector here!
            )
            await create_log_chunk(session, chunk_record)
            
            # 2. Construct and pipe the structured payload downstream over Apache Kafka
            kafka_msg = KafkaMessage(
                build_id=build_id,
                chunk_index=global_chunk_index,
                total_chunks=total_chunks_all_files,
                content=chunk_full_content,
                repo_name=repo_name
            )
            await send_log_chunk(kafka_msg)
            
            global_chunk_index += 1
            total_chunks_saved += 1
            
    # Update build status to reflect completion
    await update_build_status(session, build_id, "LOGS_FETCHED")
    print(f"Successfully chunked, saved to DB with embeddings, and streamed {total_chunks_saved} log segments to Kafka.")