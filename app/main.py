from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import admin, health
from app.routers.webhook import router as webhook_router
from app.routers.meta_auth import router as auth_router
from app.config import get_settings
from app.services.logging_service import logger

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Agent Shop - فهد")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down AI Agent Shop - فهد")

app = FastAPI(
    title="AI Agent Shop - فهد",
    description="AI-powered customer service agent for Algerian e-commerce",
    version="2.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(webhook_router)
app.include_router(auth_router)
app.include_router(admin.router)
app.include_router(health.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    return {
        "message": "مرحباً بك في نظام فهد للرد الآلي",
        "version": "2.0.0",
        "docs": "/docs",
        "admin": "/admin/"
    }


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
