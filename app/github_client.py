import httpx

from app.config import settings

class GitHubClient:
    def __init__(self):
        self.base_url = (
            f"https://api.github.com/repos/"
            f"{settings.github_owner}/{settings.github_repo}"
        )

        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        }

    async def list_issues(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/issues",
                headers=self.headers,
            )

        response.raise_for_status()
        return response.json()