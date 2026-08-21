from fastapi import FastAPI

from fastapi.responses import FileResponse

from fastapi.staticfiles import StaticFiles

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.api.auth import router as auth_router

from app.api.reports import (
    router as reports_router,
    limiter,
)

from app.core.init_db import init_db
from app.api.monitoring import (
    router as monitoring_router,
)


init_db()


app = FastAPI(
    title="ChildSafe",
    description=(
        "Digital child protection and online safety platform."
    ),
    version="0.1.0",
)


app.include_router(auth_router)

app.include_router(reports_router)

app.include_router(monitoring_router)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
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