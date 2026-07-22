import httpx
from config import settings

async def generate_embedding(text: str) -> list[float]:
    """Calls the Gemini embedding API and returns a 3072-dimensional vector."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment variables.")
        
    # Update 1: Point the URL to the working embedding model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent?key={settings.gemini_api_key}"    
    payload = {
        # Update 2: Ensure the model name matches the endpoint exactly
        "model": "models/gemini-embedding-2",
        "content": {
            "parts": [{"text": text}]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=20.0)
        
        if response.status_code != 200:
            print(f"⚠️ Embedding API Error: {response.text}")
            response.raise_for_status()
            
        data = response.json()
        return data["embedding"]["values"]