from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


class ReportCreate(BaseModel):
    platform: str
    url: str
    reason: str
    description: str


@router.post("/")
def create_report(report: ReportCreate):
    return {
        "report_id": "CV-000001",
        "status": "received",
        "message": "Report received successfully.",
        "report": report,
    }