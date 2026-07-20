from sqlalchemy.ext.asyncio import AsyncSession
from models.log_chunk import LogChunk
from repositories.log_chunk_repository import create_log_chunk
from repositories.build_repository import update_build_status

async def chunk_and_save_logs(session: AsyncSession, build_id: str, extracted_logs: dict, chunk_size: int = 500):
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
            
            chunk_record = LogChunk(
                build_id=build_id,
                chunk_index=global_chunk_index,  # Use the continuous counter
                total_chunks=total_chunks_all_files,
                content=f"--- File: {file_name} ---\n{chunk_content}"
            )
            await create_log_chunk(session, chunk_record)
            
            global_chunk_index += 1
            total_chunks_saved += 1
            
    # Update build status to reflect completion
    await update_build_status(session, build_id, "LOGS_FETCHED")
    print(f"Successfully chunked and saved {total_chunks_saved} log segments to DB.")