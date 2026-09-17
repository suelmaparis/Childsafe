from app.core.database import Base, engine

# Import every model so SQLAlchemy registers
# all tables and foreign keys in Base.metadata.

from app.models.report import Report
from app.models.report_review import ReportReview
from app.models.report_ai_analysis import ReportAIAnalysis

from app.models.reviewer import Reviewer
from app.models.reviewer_audit_log import ReviewerAuditLog

from app.models.monitoring_run import MonitoringRun
from app.models.monitoring_worker_status import (
    MonitoringWorkerStatus,
)

from app.models.report_action import ReportAction
from app.models.report_evidence import ReportEvidence


def init_db():
    Base.metadata.create_all(
        bind=engine
    )