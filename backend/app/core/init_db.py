from app.core.database import Base, engine
from app.models.report import Report


def init_db():
    Base.metadata.create_all(bind=engine)