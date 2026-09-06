import httpx
from app.config import settings
from app.models import (
    CreateIssueRequest,
    UpdateIssueRequest,
    CreateCommentRequest,
)

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

    async def create_issue(self, issue: CreateIssueRequest):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/issues",
                headers=self.headers,
                json=issue.model_dump(exclude_none=True)
            )

        response.raise_for_status()
        return _normalize_issue(response.json())

    async def get_issue(self, number: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/issues/{number}",
                headers=self.headers,
            )

        response.raise_for_status()
        return _normalize_issue(response.json())

    async def update_issue(
            self, 
            number: int, 
            issue: UpdateIssueRequest
        ):
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/issues/{number}",
                headers=self.headers,
                json=issue.model_dump(exclude_none=True),
            )

        response.raise_for_status()
        return _normalize_issue(response.json())

    async def create_comment(
        self,
        number: int,
        comment: CreateCommentRequest,
    ):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/issues/{number}/comments",
                headers=self.headers,
                json=comment.model_dump(),
            )

        response.raise_for_status()
        return _normalize_comment(response.json())

    async def list_comments(self, number: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/issues/{number}/comments",
                headers=self.headers,
            )

        response.raise_for_status()

        return [
            _normalize_comment(comment)
            for comment in response.json()
        ]



# helpers

# converts objects to strings
def _normalize_issue(data: dict) -> dict:
    return {
        "number": data["number"],
        "html_url": data["html_url"],
        "state": data["state"],
        "title": data["title"],
        "body": data["body"],
        "labels": [label["name"] for label in data["labels"]],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
    }

def _normalize_comment(data: dict) -> dict:
    return {
        "id": data["id"],
        "body": data["body"],
        "user": {
            "login": data["user"]["login"]
        },
        "created_at": data["created_at"],
        "html_url": data["html_url"],
    }