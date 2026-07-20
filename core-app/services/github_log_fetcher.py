import io
import zipfile
import asyncio
from github_client import GitHubClient
from services.s3_archive import archive_logs_to_s3

async def fetch_and_extract_logs(repo_name: str, build_id: str, logs_url: str) -> dict:
    client = GitHubClient()
    print(f"Downloading logs from GitHub...")
    zip_content = await client.download_logs(logs_url)

    # Archive to S3 in a separate thread so we don't block the async loop
    await asyncio.to_thread(archive_logs_to_s3, repo_name, build_id, zip_content)

    extracted_logs = {}
    
    # Unzip entirely in RAM
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        for file_info in z.infolist():
            if file_info.filename.endswith('.txt'):
                # Read and decode bytes to strings safely
                file_content = z.read(file_info.filename).decode('utf-8', errors='replace')
                extracted_logs[file_info.filename] = file_content

    print(f"Extracted {len(extracted_logs)} log files from archive.")
    return extracted_logs