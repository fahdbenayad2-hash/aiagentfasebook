import hmac
import hashlib
import json
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks, Query
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import get_settings
from app.services.conversation_manager import conversation_manager
from app.services.notification_service import notification_service
from app.services.logging_service import logger
import httpx

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()

webhook_limiter = Limiter(key_func=get_remote_address)


def verify_facebook_signature(payload: bytes, signature: str, app_secret: str) -> bool:
    if not signature:
        return False
    expected = hmac.new(app_secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


def sanitize_input(text: str) -> str:
    if not text:
        return ""
    return text.strip()[:2000]


@router.get("/facebook")
async def facebook_verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.FACEBOOK_VERIFY_TOKEN:
        logger.info("Facebook webhook verified successfully")
        return int(hub_challenge)
    logger.warning("Facebook webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/facebook")
@webhook_limiter.limit(settings.RATE_LIMIT_WEBHOOK)
async def facebook_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_facebook_signature(body, signature, settings.FACEBOOK_APP_SECRET):
        logger.error("Invalid Facebook webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = json.loads(body)
    logger.info(f"Received Facebook webhook with {len(data.get('entry', []))} entries")

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            if "message" in messaging:
                sender_id = messaging["sender"]["id"]
                message_text = sanitize_input(messaging["message"].get("text", ""))
                if not message_text:
                    continue

                result = await conversation_manager.process_incoming_message(
                    db, sender_id, "facebook", message_text
                )
                await _send_facebook_message(sender_id, result["response"])

                if result.get("needs_human"):
                    background_tasks.add_task(
                        notification_service.send_handoff_notification,
                        {
                            "customer_name": result.get("context_data", {}).get("name"),
                            "platform": "facebook",
                            "last_message": message_text
                        }
                    )
    return {"status": "ok"}


@router.get("/instagram")
async def instagram_verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.FACEBOOK_VERIFY_TOKEN:
        logger.info("Instagram webhook verified successfully")
        return int(hub_challenge)
    logger.warning("Instagram webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/instagram")
@webhook_limiter.limit(settings.RATE_LIMIT_WEBHOOK)
async def instagram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    body = await request.body()
    data = json.loads(body)
    logger.info(f"Received Instagram webhook with {len(data.get('entry', []))} entries")

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            if "message" in messaging:
                sender_id = messaging["sender"]["id"]
                message_text = sanitize_input(messaging["message"].get("text", ""))
                if not message_text:
                    continue

                result = await conversation_manager.process_incoming_message(
                    db, sender_id, "instagram", message_text
                )
                await _send_instagram_message(sender_id, result["response"])

                if result.get("needs_human"):
                    background_tasks.add_task(
                        notification_service.send_handoff_notification,
                        {
                            "platform": "instagram",
                            "last_message": message_text
                        }
                    )
    return {"status": "ok"}


async def _send_facebook_message(recipient_id: str, message: str):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={settings.FACEBOOK_PAGE_ACCESS_TOKEN}"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "recipient": {"id": recipient_id},
            "message": {"text": message[:2000]}
        })


async def _send_instagram_message(recipient_id: str, message: str):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={settings.FACEBOOK_PAGE_ACCESS_TOKEN}"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "recipient": {"id": recipient_id},
            "message": {"text": message[:2000]}
        })
