from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import require_role
from app.core import settings
from app.models.reviewer import Reviewer


router = APIRouter(
    prefix="/media",
    tags=["Media Analysis"],
)


@router.get("/status")
def media_analysis_status(
    current_reviewer: Reviewer = Depends(
        require_role(
            "admin",
            "senior_reviewer",
        )
    ),
):
    """
    Return the current media-analysis availability.

    Only administrators and senior reviewers
    can access this endpoint.
    """

    if not settings.MEDIA_ANALYSIS_ENABLED:
        return {
            "enabled": False,
            "status": "disabled",
        }

    return {
        "enabled": True,
        "status": "available",
    }