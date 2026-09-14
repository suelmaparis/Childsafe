from app.core.database import Base, engine
from app.models.report import Report
from app.models.monitoring_run import MonitoringRun
from app.models.report_action import ReportAction
from app.models.report_evidence import ReportEvidence


def init_db():
    Base.metadata.create_all(bind=engine)