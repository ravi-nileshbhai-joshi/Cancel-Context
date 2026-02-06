from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import admin, cancel, dashboard
from app.config import settings
from app.database import Base, engine
from app.utils.logging import configure_logging

configure_logging()

if settings.sentry_dsn:
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=settings.sentry_traces_sample_rate,
        )
    except Exception as exc:
        print(f"Sentry initialization failed: {exc}")

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)


app.include_router(cancel.router)
app.include_router(dashboard.router)
app.include_router(admin.router)

BASE_DIR = Path(__file__).resolve().parents[1]
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/api/health")
def health():
    return {"status": "ok"}
