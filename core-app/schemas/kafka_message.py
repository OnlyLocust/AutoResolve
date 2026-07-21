from pydantic import BaseModel

class KafkaMessage(BaseModel):
    build_id: str
    chunk_index: int
    total_chunks: int
    content: str
    repo_name: str