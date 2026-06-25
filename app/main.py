from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager
from app.database import engine, Base, run_migration
from app.routers import admin, health
from app.routers.auth import router as auth_router
from app.routers.webhook import router as webhook_router
from app.routers.api import router as api_router
from app.config import get_settings
from app.services.logging_service import logger

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MARIA")
    Base.metadata.create_all(bind=engine)
    run_migration()

    async def _token_health_loop():
        while True:
            try:
                from app.services.facebook_oauth import daily_token_health_check
                await daily_token_health_check()
            except Exception as e:
                logger.error(f"Token health check error: {e}")
            await asyncio.sleep(86400)

    task = asyncio.create_task(_token_health_loop())
    logger.info("Token health monitoring started (runs every 24h)")

    yield

    task.cancel()
    logger.info("Shutting down MARIA")

app = FastAPI(
    title="MARIA - AI Agent Shop",
    description="AI-powered customer service agent for Algerian e-commerce",
    version="2.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "https://maria-store.vercel.app",
        "https://poetic-patience-production.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(webhook_router)
app.include_router(auth_router)
app.include_router(api_router)
app.include_router(admin.router)
app.include_router(health.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

assets_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist" / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    index_path = Path(__file__).resolve().parent.parent / "frontend" / "dist" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "message": "مرحباً بك في MARIA للرد الآلي",
        "version": "2.0.0",
        "docs": "/docs",
        "admin": "/admin/"
    }


@app.get("/admin/")
async def admin_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")


@app.get("/admin")
async def admin_redirect_no_slash():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")


@app.get("/privacy")
async def privacy():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/privacy.html")


@app.get("/terms")
async def terms():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/terms.html")


@app.get("/data-deletion")
async def data_deletion_page():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/privacy.html")


@app.post("/data-deletion")
async def data_deletion(request: Request):
    from app.database import get_db, SessionLocal
    data = await request.json()
    psid = data.get("entry", [{}])[0].get("messaging", [{}])[0].get("sender", {}).get("id", "")
    if psid:
        db = SessionLocal()
        try:
            from app.models import Customer, Conversation
            db.query(Conversation).filter(Conversation.customer_id == psid).delete()
            db.query(Customer).filter(Customer.facebook_psid == psid).delete()
            db.commit()
        finally:
            db.close()
    return {
        "url": "/data-deletion",
        "confirmation_code": psid or "unknown"
    }


@app.get("/{path:path}")
async def spa_fallback(path: str):
    from fastapi.responses import FileResponse
    api_prefixes = ("api/", "admin/", "webhooks/")
    if path.startswith(api_prefixes) or "." in path or path in ("docs", "openapi.json", "redoc", "privacy", "terms", "data-deletion"):
        raise HTTPException(status_code=404)
    index_path = Path(__file__).resolve().parent.parent / "frontend" / "dist" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    raise HTTPException(status_code=404)
