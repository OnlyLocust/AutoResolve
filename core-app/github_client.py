import httpx
from config import settings

class GitHubClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        # 30s connect, 60s read timeout
        self.timeout = httpx.Timeout(60.0, connect=30.0)

    async def download_logs(self, url: str) -> bytes:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            # GitHub's logs endpoint returns a binary zip file
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()

            # Rate limit check
            remaining = int(response.headers.get("X-RateLimit-Remaining", 100))
            if remaining < 100:
                print(f"Warning: GitHub API Rate Limit low ({remaining} remaining).")

            return response.content