import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.config import settings
from app.services.logging_service import logger

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt, h = stored.split(":", 1)
        return hmac.compare_digest(hashlib.sha256((salt + password).encode()).hexdigest(), h)
    except Exception:
        return False


def _create_token(user_id: int) -> str:
    payload = f"{user_id}:{datetime.now(timezone.utc).timestamp() + 86400 * 7}:{secrets.token_hex(8)}"
    sig = hashlib.sha256((payload + settings.APP_SECRET_KEY).encode()).hexdigest()[:16]
    return f"{payload}:{sig}"


def _decode_token(token: str) -> Optional[int]:
    try:
        parts = token.split(":")
        if len(parts) < 4:
            return None
        user_id = int(parts[0])
        expires = float(parts[1])
        sig = parts[-1]
        payload = ":".join(parts[:-1])
        expected = hashlib.sha256((payload + settings.APP_SECRET_KEY).encode()).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected):
            return None
        if datetime.now(timezone.utc).timestamp() > expires:
            return None
        return user_id
    except (ValueError, IndexError):
        return None


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization[7:]
    user_id = _decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    credits: int

    class Config:
        from_attributes = True


@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not _verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة")
    token = _create_token(user.id)
    return {"token": token, "user": UserResponse.model_validate(user)}


@router.post("/register", response_model=UserResponse)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="البريد الإلكتروني مستخدم بالفعل")
    user = User(
        name=req.name,
        email=req.email,
        phone=req.phone,
        password_hash=_hash_password(req.password),
        credits=5000,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user registered: {user.email}")
    return user


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
