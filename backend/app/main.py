import threading
from contextlib import asynccontextmanager

from app.monitoring.scheduler import monitoring_scheduler_loop
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api import chat

from slowapi import (
    _rate_limit_exceeded_handler,
)
from slowapi.errors import RateLimitExceeded

from app.api.auth import (
    router as auth_router,
)

from app.api.reports import (
    router as reports_router,
    limiter,
)

from app.api.monitoring import (
    router as monitoring_router,
)

from app.core.init_db import init_db

from slowapi.errors import RateLimitExceeded

init_db()
@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = threading.Event()

    scheduler_thread = threading.Thread(
        target=monitoring_scheduler_loop,
        args=(stop_event,),
        daemon=True,
        name="childsafe-monitoring-scheduler",
    )

    scheduler_thread.start()

    try:
        yield
    finally:
        stop_event.set()
        scheduler_thread.join(timeout=5)


app = FastAPI(
    title="ChildSafe",
    description=(
        "Digital child protection "
        "and online safety platform."
    ),
    version="0.1.0",
    lifespan=lifespan,
)



app.include_router(
    auth_router
)

app.include_router(
    reports_router
)
app.include_router(
    chat.router
)

app.include_router(
    monitoring_router
)


app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


app.mount(
    "/static",
    StaticFiles(
        directory="app/static"
    ),
    name="static",
)


@app.get("/")
def public_home():
    return FileResponse(
        "app/static/report/index.html"
    )


@app.get("/admin")
def admin_dashboard():
    return FileResponse(
        "app/static/admin/index.html"
    )

@app.get("/privacy", include_in_schema=False)
def privacy_policy():
    return FileResponse(
        "app/static/legal/privacy.html"
    )