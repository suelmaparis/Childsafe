from app.core.database import Base, engine
from app.models.report import Report
from app.models.monitoring_run import MonitoringRun


def init_db():
    Base.metadata.create_all(bind=engine)