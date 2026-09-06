import hashlib
import hmac
from fastapi import HTTPException
from app.config import settings

ISSUE_ACTIONS = {
    "opened",
    "edited",
    "closed",
    "reopened",
}

COMMENT_ACTIONS = {
    "created",
    "edited",
    "deleted",
}

def verify_signature(
    body: bytes,
    signature: str | None,
):
    if not signature:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook signature",
        )

    expected_signature = (
        "sha256="
        + hmac.new(
            settings.webhook_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(
        expected_signature,
        signature,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

def validate_event(event: str | None, action: str | None):
    if event == "ping":
        return

    if event == "issues":
        if action not in ISSUE_ACTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown issues action: {action}",
            )
        return

    if event == "issue_comment":
        if action not in COMMENT_ACTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown issue_comment action: {action}",
            )
        return

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported webhook event: {event}",
    )