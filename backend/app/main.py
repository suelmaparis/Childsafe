from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.reports import router as reports_router
from app.core.init_db import init_db


init_db()


app = FastAPI(
    title="ChildSafe",
    description="Digital child protection and online safety platform.",
    version="0.1.0",
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


app.include_router(auth_router)
app.include_router(reports_router)


@app.get("/")
def root():
    return {
        "message": "ChildSafe API",
        "status": "online",
    }


@app.get("/admin")
def admin_dashboard():
    return FileResponse(
        "app/static/admin/index.html"
    )