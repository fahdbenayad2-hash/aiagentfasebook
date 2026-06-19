import secrets
import httpx
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import PlatformAccount
from app.services.logging_service import logger


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def auth_login():
    state = secrets.token_urlsafe(16)
    redirect = "https://www.facebook.com/{}/dialog/oauth".format(settings.FB_API_VERSION or "v18.0")
    params = (
        f"client_id={settings.FB_APP_ID}"
        f"&redirect_uri={settings.FB_REDIRECT_URI}"
        f"&state={state}"
        f"&scope=pages_messaging,pages_show_list,pages_manage_metadata,instagram_basic,instagram_manage_messages"
        f"&response_type=code"
    )
    return RedirectResponse(url=f"{redirect}?{params}")


@router.get("/callback")
async def auth_callback(code: str = None, state: str = None, error: str = None, db: Session = Depends(get_db)):
    if error:
        raise HTTPException(status_code=400, detail=f"Meta OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    token_url = "https://graph.facebook.com/{}/oauth/access_token".format(settings.FB_API_VERSION or "v18.0")
    async with httpx.AsyncClient() as client:
        resp = await client.get(token_url, params={
            "client_id": settings.FB_APP_ID,
            "client_secret": settings.FB_APP_SECRET,
            "redirect_uri": settings.FB_REDIRECT_URI,
            "code": code
        })
        data = resp.json()

    if "access_token" not in data:
        logger.error(f"Token exchange failed: {data}")
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {data.get('error', {}).get('message', 'unknown')}")

    user_token = data["access_token"]

    # Exchange for long-lived token
    async with httpx.AsyncClient() as client:
        long_resp = await client.get(token_url, params={
            "grant_type": "fb_exchange_token",
            "client_id": settings.FB_APP_ID,
            "client_secret": settings.FB_APP_SECRET,
            "fb_exchange_token": user_token
        })
        long_data = long_resp.json()

    long_token = long_data.get("access_token", user_token)

    # Get user's pages
    async with httpx.AsyncClient() as client:
        pages_resp = await client.get(
            "https://graph.facebook.com/{}/me/accounts".format(settings.FB_API_VERSION or "v18.0"),
            params={"access_token": long_token}
        )
        pages_data = pages_resp.json()

    saved_pages = []
    for page in pages_data.get("data", []):
        page_id = page["id"]
        page_token = page["access_token"]
        page_name = page.get("name", "")

        ig_id = None
        try:
            async with httpx.AsyncClient() as client:
                ig_resp = await client.get(
                    "https://graph.facebook.com/{}/{}".format(settings.FB_API_VERSION or "v18.0", page_id),
                    params={"access_token": page_token, "fields": "instagram_business_account{id}"}
                )
                ig_data = ig_resp.json()
                if "instagram_business_account" in ig_data:
                    ig_id = ig_data["instagram_business_account"]["id"]
        except Exception as e:
            logger.warning(f"Could not fetch IG for page {page_id}: {e}")

        existing = db.query(PlatformAccount).filter(
            PlatformAccount.page_id == page_id
        ).first()

        if existing:
            existing.access_token = page_token
            if ig_id:
                existing.ig_id = ig_id
        else:
            acc = PlatformAccount(
                platform="facebook",
                page_id=page_id,
                page_name=page_name,
                ig_id=ig_id,
                access_token=page_token,
                active=True
            )
            db.add(acc)

        saved_pages.append({"id": page_id, "name": page_name, "ig_id": ig_id})
        db.commit()

    html = """<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>تم الربط بنجاح</title>
<style>
body{font-family:Arial,sans-serif;max-width:600px;margin:40px auto;padding:0 20px;text-align:center;direction:rtl}
h1{color:#28a745}.page{border:1px solid #ddd;border-radius:8px;padding:12px;margin:10px 0;text-align:right}
.check{color:#28a745;font-size:20px}.btn{display:inline-block;padding:10px 20px;background:#1877f2;color:#fff;text-decoration:none;border-radius:6px;margin-top:20px}
</style></head><body>
<h1>✅ تم الربط بنجاح!</h1>
<p>الصفحات المرتبطة:</p>
"""
    for p in saved_pages:
        html += f'<div class="page"><span class="check">✔</span> <strong>{p["name"]}</strong>'
        if p["ig_id"]:
            html += f'<br><small>📸 إنستغرام: {p["ig_id"]}</small>'
        html += "</div>"

    html += '<a class="btn" href="/admin/">→ لوحة التحكم</a></body></html>'
    return HTMLResponse(content=html, status_code=200)
