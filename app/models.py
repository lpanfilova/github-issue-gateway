from pydantic import BaseModel, ConfigDict
from datetime import datetime

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