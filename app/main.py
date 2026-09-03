from fastapi import FastAPI, Response, status
from app.config import settings
from app.github_client import GitHubClient
from app.models import CreateIssueRequest, Issue, UpdateIssueRequest

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

@app.get("/issues/{number}", response_model=Issue)
async def get_issue(number: int):
    return await github.get_issue(number)

@app.post(
    "/issues", 
    status_code=status.HTTP_201_CREATED,
    response_model=Issue,
)
async def create_issue(issue: CreateIssueRequest, response: Response):
    created = await github.create_issue(issue)
    response.headers["Location"] = f"/issues/{created['number']}"

    return created

@app.patch("/issues/{number}", response_model=Issue)
async def update_issue(number: int, issue: UpdateIssueRequest):
    return await github.update_issue(number, issue)