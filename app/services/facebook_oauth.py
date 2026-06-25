import secrets
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional
from cryptography.fernet import Fernet
from app.config import settings
from app.services.logging_service import logger
from app.database import SessionLocal
from app.models import FacebookConnection


def _get_fernet() -> Fernet:
    key = settings.TOKEN_ENCRYPTION_KEY
    if not key:
        key = Fernet.generate_key().decode()
        logger.warning("TOKEN_ENCRYPTION_KEY not set — generated ephemeral key. "
                       "Tokens will be lost on restart. Set TOKEN_ENCRYPTION_KEY in .env")
        settings.TOKEN_ENCRYPTION_KEY = key
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


def encrypt_token(plain: str) -> str:
    return _get_fernet().encrypt(plain.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()


def mask_token(token: str) -> str:
    if not token or len(token) < 10:
        return "***"
    return token[:10] + "..."


async def exchange_code_for_token(code: str, redirect_uri: str) -> str:
    url = f"https://graph.facebook.com/{settings.FB_API_VERSION}/oauth/access_token"
    params = {
        "client_id": settings.FB_APP_ID,
        "client_secret": settings.FB_APP_SECRET or settings.FACEBOOK_APP_SECRET,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    token = data.get("access_token")
    if not token:
        raise ValueError(f"Facebook code exchange failed: {data}")
    logger.info(f"OAuth: code exchanged for short-lived token {mask_token(token)}")
    return token


async def exchange_for_long_lived(short_token: str) -> tuple[str, int]:
    url = f"https://graph.facebook.com/{settings.FB_API_VERSION}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": settings.FB_APP_ID,
        "client_secret": settings.FB_APP_SECRET or settings.FACEBOOK_APP_SECRET,
        "fb_exchange_token": short_token,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    long_token = data.get("access_token")
    expires_in = data.get("expires_in", 0)
    if not long_token:
        raise ValueError(f"Facebook long-lived exchange failed: {data}")
    logger.info(f"OAuth: long-lived user token obtained, expires in {expires_in}s")
    return long_token, expires_in


async def get_user_pages(user_token: str) -> list[dict]:
    url = f"https://graph.facebook.com/{settings.FB_API_VERSION}/me/accounts"
    params = {
        "access_token": user_token,
        "fields": "id,name,access_token,tasks,picture",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    pages = data.get("data", [])
    logger.info(f"OAuth: found {len(pages)} pages for user")
    return pages


async def get_token_info(token: str) -> dict:
    app_token = f"{settings.FB_APP_ID}|{settings.FB_APP_SECRET or settings.FACEBOOK_APP_SECRET}"
    url = "https://graph.facebook.com/debug_token"
    params = {
        "input_token": token,
        "access_token": app_token,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


async def upsert_facebook_connection(
    page_id: str,
    page_name: str,
    page_access_token: str,
    user_access_token: Optional[str] = None,
    user_token_expires_at: Optional[datetime] = None,
    store_name: Optional[str] = None,
) -> FacebookConnection:
    db = SessionLocal()
    try:
        existing = db.query(FacebookConnection).filter(
            FacebookConnection.page_id == page_id
        ).first()
        if existing:
            existing.page_name = page_name
            existing.page_access_token_encrypted = encrypt_token(page_access_token)
            if user_access_token:
                existing.user_access_token_encrypted = encrypt_token(user_access_token)
            if user_token_expires_at:
                existing.user_token_expires_at = user_token_expires_at
            if store_name:
                existing.store_name = store_name
            existing.is_active = True
        else:
            existing = FacebookConnection(
                page_id=page_id,
                page_name=page_name,
                page_access_token_encrypted=encrypt_token(page_access_token),
                user_access_token_encrypted=encrypt_token(user_access_token) if user_access_token else None,
                user_token_expires_at=user_token_expires_at,
                store_name=store_name or page_name,
            )
            db.add(existing)
        db.commit()
        db.refresh(existing)
        logger.info(f"OAuth: saved connection for page '{page_name}' ({page_id})")
        return existing
    finally:
        db.close()


async def get_active_page_token(page_id: Optional[str] = None) -> Optional[str]:
    db = SessionLocal()
    try:
        query = db.query(FacebookConnection).filter(FacebookConnection.is_active == True)
        if page_id:
            query = query.filter(FacebookConnection.page_id == page_id)
        conn = query.first()
        if conn:
            return decrypt_token(conn.page_access_token_encrypted)
        return None
    finally:
        db.close()


async def get_active_connections() -> list[FacebookConnection]:
    db = SessionLocal()
    try:
        return db.query(FacebookConnection).filter(
            FacebookConnection.is_active == True
        ).order_by(FacebookConnection.page_name).all()
    finally:
        db.close()


async def delete_connection(conn_id: int) -> bool:
    db = SessionLocal()
    try:
        conn = db.query(FacebookConnection).filter(FacebookConnection.id == conn_id).first()
        if not conn:
            return False
        db.delete(conn)
        db.commit()
        logger.info(f"OAuth: deleted connection for page '{conn.page_name}' ({conn.page_id})")
        return True
    finally:
        db.close()


async def daily_token_health_check():
    from app.services.notification_service import send_telegram_notification
    connections = await get_active_connections()
    for conn in connections:
        try:
            page_token = decrypt_token(conn.page_access_token_encrypted)
            info = await get_token_info(page_token)
            if not info.get("data", {}).get("is_valid", False):
                await send_telegram_notification(
                    f"🚨 توكن {conn.page_name} ما عادش صالح!\n"
                    f"روح لـ /admin/facebook/connections وعاود ربط الصفحة"
                )
        except Exception as e:
            logger.error(f"Token health check failed for {conn.page_name}: {e}")

        if conn.user_token_expires_at and conn.user_access_token_encrypted:
            remaining = (conn.user_token_expires_at - datetime.now(timezone.utc).replace(tzinfo=None)).days
            if remaining < 10:
                await send_telegram_notification(
                    f"⚠️ توكن المستخدم لـ {conn.page_name} يخلص في {remaining} أيام\n"
                    f"روح لـ /admin/facebook/connect وعاود ربط الصفحة"
                )


CSRF_TOKENS: dict[str, datetime] = {}


def generate_csrf_token() -> str:
    token = secrets.token_urlsafe(32)
    CSRF_TOKENS[token] = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=15)
    return token


def verify_csrf_token(token: str) -> bool:
    expiry = CSRF_TOKENS.pop(token, None)
    if not expiry:
        return False
    if datetime.now(timezone.utc).replace(tzinfo=None) > expiry:
        return False
    return True
