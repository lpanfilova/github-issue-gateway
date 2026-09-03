from fastapi import FastAPI
from app.config import settings
from app.github_client import GitHubClient

app = FastAPI(
    title="GitHub Issue Gateway",
    version="0.0.1"
)

github = GitHubClient()

@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "repository": f"{settings.github_owner}/{settings.github_repo}",
    }

@app.get("/issues")
async def list_issues():
    return await github.list_issues()