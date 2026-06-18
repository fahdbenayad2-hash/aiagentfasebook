from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import webhooks, admin, health
from app.config import get_settings
from app.services.logging_service import logger

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Agent Shop - أمين")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down AI Agent Shop - أمين")

app = FastAPI(
    title="AI Agent Shop - أمين",
    description="AI-powered customer service agent for Algerian e-commerce",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(webhooks.router)
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
        "message": "مرحباً بك في نظام أمين للرد الآلي",
        "docs": "/docs",
        "admin": "/admin/"
    }
