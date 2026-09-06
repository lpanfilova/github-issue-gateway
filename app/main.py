from fastapi import FastAPI, Query, Request, Response, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Literal
import json
from app.webhooks import verify_signature, validate_event
from app.config import settings
from app.github_client import GitHubClient
from app.models import (
    CreateIssueRequest,
    UpdateIssueRequest,
    Issue,
    CreateCommentRequest,
    Comment,
)

app = FastAPI(
    title="GitHub Issue Gateway",
    version="0.0.1"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({
            "detail":exc.errors()
        })
    )

github = GitHubClient()

@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "repository": f"{settings.github_owner}/{settings.github_repo}",
    }

@app.get("/issues", response_model=list[Issue])
async def list_issues(
    response: Response,
    state: Literal["open", "closed", "all"] = "open",
    labels: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=100),
):
    issues, link = await github.list_issues(
        state=state,
        labels=labels,
        page=page,
        per_page=per_page,
    )

    if link:
        response.headers["Link"] = link

    return issues

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

@app.post(
    "/issues/{number}/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=Comment,
)
async def create_comment(
    number: int,
    comment: CreateCommentRequest,
):
    return await github.create_comment(number, comment)

@app.get(
    "/issues/{number}/comments",
    response_model=list[Comment],
)
async def list_comments(number: int):
    return await github.list_comments(number)

@app.post("/webhook", status_code=204)
async def webhook(request: Request):
    body = await request.body()

    signature = request.headers.get(
        "X-Hub-Signature-256"
    )

    verify_signature(body, signature)

    event = request.headers.get(
        "X-GitHub-Event"
    )

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        )

    action = payload.get("action")

    validate_event(event, action)

    return Response(status_code=204)