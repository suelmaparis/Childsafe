from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_chat import generate_chat_reply
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.reports import (
    ReportCreate,
    create_report_record,
    limiter,
)
from fastapi import Request
from app.models.report import Report
from sqlalchemy.exc import IntegrityError
from app.models.report import Report

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatHistoryItem(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=2000)


class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatHistoryItem] = Field(
        default_factory=list,
        max_length=10,
    )


@router.post("/message")
@limiter.limit("10/minute")
def receive_chat_message(
    request: Request,
    data: ChatMessage,
):
    try:
        reply = generate_chat_reply(
    message=data.message,
    history=[
        item.model_dump()
        for item in data.history
        if item.role in ("user", "assistant")
    ],
)

        return {
            "reply": reply,
            "status": "received",
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="O assistente está temporariamente indisponível. Tenta novamente mais tarde.",
        )
def create_chat_report(
    description: str,
    submission_id: str,
    db: Session,
):
    report = ReportCreate(
        platform="Other",
        url="",
        reason="potential_child_risk",
        description=description,
        source_type="chat_report",
        source_channel="public_ai_chat",
        source_reference=submission_id,
    )

    return create_report_record(
        report=report,
        db=db,
    )

class ChatReportRequest(BaseModel):
    description: str = Field(
        min_length=20,
        max_length=5000,
    )
    confirmed: bool = False
    submission_id: str = Field(
        min_length=16,
        max_length=100,
    )

@router.post("/report")
@limiter.limit("5/minute")

def submit_chat_report(
    request: Request,
    data: ChatReportRequest,
    db: Session = Depends(get_db),
):
    if not data.confirmed:
        raise HTTPException(
            status_code=400,
            detail="É necessário confirmar o envio da denúncia.",
        )
    existing_report = (
    db.query(Report)
    .filter(
        Report.source_type == "chat_report",
        Report.source_channel == "public_ai_chat",
        Report.source_reference == data.submission_id,
    )
    .first()
)

    if existing_report:
        return {
            "report_id": f"CV-{existing_report.id:06d}",
            "status": existing_report.status,
            "message": "Esta denúncia já foi recebida pelo ChildSafe.",
        }
    try:
        result = create_chat_report(
            description=data.description,
            submission_id=data.submission_id,
            db=db,
        )
    except IntegrityError:
        db.rollback()

        existing_report = (
            db.query(Report)
            .filter(
                Report.source_type == "chat_report",
                Report.source_channel == "public_ai_chat",
                Report.source_reference == data.submission_id,
            )
            .first()
        )

        if existing_report is None:
            raise

        result = {
            "report_id": f"CV-{existing_report.id:06d}",
            "status": existing_report.status,
        }

    return {
        "report_id": result["report_id"],
        "status": result["status"],
        "message": "Denúncia recebida pelo ChildSafe.",
    }