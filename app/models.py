from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal

class CreateIssueRequest(BaseModel):
    title: str
    body: str | None = None
    labels: list[str] | None = None

class Issue(BaseModel):
    number: int
    html_url: str
    state: str
    title: str
    body: str | None
    labels: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(extra="ignore")

class UpdateIssueRequest(BaseModel):
    title: str | None = None
    body: str | None = None
    state: Literal["open", "closed"] | None = None

class CreateCommentRequest(BaseModel):
    body: str

class CommentUser(BaseModel):
    login: str

class Comment(BaseModel):
    id: int
    body: str
    user: CommentUser
    created_at: datetime
    html_url: str