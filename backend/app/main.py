from fastapi import FastAPI

from app.api.reports import router as reports_router
from app.core.init_db import init_db


init_db()


app = FastAPI(
    title="ChildSafe",
    description="Digital child protection and online safety platform.",
    version="0.1.0",
)


app.include_router(reports_router)


@app.get("/")
def root():
    return {
        "message": "ChildSafe API",
        "status": "online",
    }