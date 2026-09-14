import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from piccolo.engine import engine_finder, Engine

from src.apps.tasks import routes as tasks_routes
from src.apps.tasks.models import Task


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine: Optional[Engine] = engine_finder()

    if engine is None:
        raise RuntimeError("no engine found")

    await engine.start_connection_pool()
    yield
    await engine.close_connection_pool()


app = FastAPI(lifespan=lifespan)
app.include_router(tasks_routes.router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - start) * 1000:.2f}"
    return response


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    try:
        await Task.count()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok"}
