import httpx
import time
from fastapi import HTTPException
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

    async def list_issues(
        self,
        state: str = "open",
        labels: str | None = None,
        page: int = 1,
        per_page: int = 30
        ):

        params = {
            "state": state,
            "page": page,
            "per_page": per_page,
        }

        if labels:
            params["labels"] = labels

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/issues",
                headers=self.headers,
                params=params,
            )

        _handle_github_error(response)

        issues = [
            _normalize_issue(issue)
            for issue in response.json()
        ]

        link = response.headers.get("Link")

        return issues, link

    async def create_issue(self, issue: CreateIssueRequest):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/issues",
                headers=self.headers,
                json=issue.model_dump(exclude_none=True)
            )

        _handle_github_error(response)
        return _normalize_issue(response.json())

    async def get_issue(self, number: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/issues/{number}",
                headers=self.headers,
            )

        _handle_github_error(response)
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

        _handle_github_error(response)
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

        _handle_github_error(response)
        return _normalize_comment(response.json())

    async def list_comments(self, number: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/issues/{number}/comments",
                headers=self.headers,
            )

        _handle_github_error(response)

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

def _handle_github_error(response: httpx.Response):
    if response.is_success:
        return

    try:
        message = response.json().get("message", "GitHub API error")
    except ValueError:
        message = "GitHub API error"

    if response.status_code in (403,429):
        remaining =response.headers.get("X-RateLimit-Remaining")
        retry_after = response.headers.get("Retry-After")

        if remaining == "0" or retry_after:
            if not retry_after:
                reset = int(response.headers.get("X-RateLimit-Reset", 0))
                retry_after = str(max(1, reset - int(time.time())))

            raise HTTPException(
                status_code=429,
                detail=f"GitHub rate limit exceeded: {message}",
                headers={"Retry-After": retry_after},
            )

    if response.status_code == 401:
        raise HTTPException(
            status_code=401,
            detail=f"GitHub authentication failed: {message}",
        )

    if response.status_code == 403:
        raise HTTPException(
            status_code=403,
            detail=f"GitHub access forbidden: {message}",
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=f"GitHub resource not found: {message}",
        )

    if response.status_code == 422:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub rejected the request: {message}",
        )

    if response.status_code >= 500:
        raise HTTPException(
            status_code=503,
            detail="GitHub service is temporarily unavailable",
        )

    raise HTTPException(
        status_code=400,
        detail=f"GitHub API error: {message}",
    )