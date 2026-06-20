import json
import hmac
import hashlib
import httpx
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from app.services.conversation_manager import conversation_manager
from app.services.notification_service import notification_service
from app.services.logging_service import logger


router = APIRouter(prefix="/webhooks", tags=["webhooks"])

_pending_handoffs: dict[int, str] = {}


def sanitize_input(text: str) -> str:
    if not text:
        return ""
    return text.strip()[:2000]


@router.get("/facebook")
async def verify_facebook_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    from app.config import settings
    expected = settings.FB_VERIFY_TOKEN or settings.FACEBOOK_VERIFY_TOKEN
    if hub_mode == "subscribe" and hub_verify_token == expected:
        logger.info("Facebook webhook verified")
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/facebook")
async def receive_facebook_webhook(request: Request):
    from app.config import settings
    from app.database import get_db
    from app.models import PlatformAccount
    from fastapi import Depends

    body = await request.body()
    data = json.loads(body)
    logger.info(f"Received Facebook webhook with {len(data.get('entry', []))} entries")

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            if "message" in messaging:
                sender_id = messaging["sender"]["id"]
                recipient_id = messaging.get("recipient", {}).get("id", "")
                message_text = sanitize_input(messaging["message"].get("text", ""))
                if not message_text:
                    continue

                db = next(get_db())
                try:
                    token = None
                    if recipient_id:
                        account = db.query(PlatformAccount).filter(
                            PlatformAccount.page_id == recipient_id,
                            PlatformAccount.active == True
                        ).first()
                        if account:
                            token = account.access_token

                    if not token:
                        token = settings.FB_PAGE_ACCESS_TOKEN or settings.FACEBOOK_PAGE_ACCESS_TOKEN

                    result = await conversation_manager.process_incoming_message(
                        db, sender_id, "facebook", message_text
                    )
                    await _send_messenger_message(sender_id, result["response"], token)

                    if result.get("needs_human"):
                        import asyncio
                        from app.config import settings
                        staff = int(settings.TELEGRAM_STAFF_CHAT_ID) if settings.TELEGRAM_STAFF_CHAT_ID else None
                        if staff:
                            _pending_handoffs[staff] = sender_id
                        asyncio.ensure_future(
                            notification_service.send_handoff_notification({
                                "customer_name": result.get("context_data", {}).get("name"),
                                "platform": "facebook",
                                "last_message": message_text
                            })
                        )
                except Exception as e:
                    logger.error(f"Error processing Facebook message: {e}")
                finally:
                    db.close()

    return {"status": "ok"}


@router.get("/instagram")
async def verify_instagram_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    from app.config import settings
    expected = settings.FB_VERIFY_TOKEN or settings.FACEBOOK_VERIFY_TOKEN
    if hub_mode == "subscribe" and hub_verify_token == expected:
        logger.info("Instagram webhook verified")
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/instagram")
async def receive_instagram_webhook(request: Request):
    logger.info("Instagram webhook disabled — only Facebook Messenger is active")
    return {"status": "ok"}


@router.post("/telegram")
async def receive_telegram_webhook(request: Request):
    from app.config import settings
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return {"status": "ok"}
    staff_chat_id = int(settings.TELEGRAM_STAFF_CHAT_ID) if settings.TELEGRAM_STAFF_CHAT_ID else None
    if not staff_chat_id:
        logger.warning("TELEGRAM_STAFF_CHAT_ID not configured")
        return {"status": "ok"}

    body = await request.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = sanitize_input(message.get("text", ""))
    if not chat_id or not text:
        return {"status": "ok"}

    if chat_id != staff_chat_id:
        logger.warning(f"Unauthorized Telegram chat_id: {chat_id}")
        return {"status": "ok"}

    if text == "/start":
        await _send_telegram_message(chat_id, "مرحباً بك في نظام الرد الآلي. رسائلك راح تتحول للزبون اللي مسجل في طلب التحويل.")
        return {"status": "ok"}

    psid = _pending_handoffs.pop(staff_chat_id, None)
    if not psid:
        await _send_telegram_message(chat_id, "ماكاش تحويل نشط دابا. استنى حتى يطلب زبون التحويل لموظف بشري.")
        return {"status": "ok"}

    await _send_messenger_message(psid, f"[موظف بشري] {text}", None)
    await _send_telegram_message(chat_id, "تم إرسال ردك للزبون ✅")
    logger.info(f"Staff reply forwarded to Facebook PSID {psid}")
    return {"status": "ok"}


async def _send_messenger_message(recipient_id: str, message: str, access_token: str = None):
    from app.config import settings
    token = access_token or settings.FB_PAGE_ACCESS_TOKEN or settings.FACEBOOK_PAGE_ACCESS_TOKEN
    if not token:
        logger.error("No Facebook access token configured")
        return
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={token}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "recipient": {"id": recipient_id},
            "message": {"text": message[:2000]}
        })
        if response.status_code != 200:
            logger.error(f"Send failed: {response.status_code} {response.text}")


async def _send_telegram_message(chat_id: int, message: str):
    from app.config import settings
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("No Telegram bot token configured")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": message[:4096],
            "parse_mode": "HTML"
        })
