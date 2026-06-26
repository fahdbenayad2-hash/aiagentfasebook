import json
import hmac
import hashlib
import httpx
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
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
    from app.core.dispatcher import handle_event
    from app.models.facebook import MessagingEvent
    from app.core.session import session_manager

    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    app_secret = settings.FB_APP_SECRET or settings.FACEBOOK_APP_SECRET
    if app_secret:
        expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(f"sha256={expected}", signature):
            logger.error("Invalid Facebook webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

    data = json.loads(body)
    logger.info(f"Received Facebook webhook with {len(data.get('entry', []))} entries")

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            event = MessagingEvent(**messaging)
            try:
                await handle_event(event)
            except Exception as e:
                logger.error(f"Error processing Facebook message: {e}")

            if event.message and event.message.text:
                from app.core.session import session_manager
                state = await session_manager.get_or_create(
                    event.sender.get("id", ""),
                    event.recipient.get("id", "")
                )
                if state and state.escalation_requested:
                    _pending_handoffs_list = []
                    if settings.TELEGRAM_ADMIN_CHAT_IDS:
                        for cid in settings.TELEGRAM_ADMIN_CHAT_IDS.split(","):
                            try:
                                _pending_handoffs_list.append(int(cid.strip()))
                            except ValueError:
                                pass
                    if settings.TELEGRAM_STAFF_CHAT_ID:
                        try:
                            cid = int(settings.TELEGRAM_STAFF_CHAT_ID)
                            if cid not in _pending_handoffs_list:
                                _pending_handoffs_list.append(cid)
                        except ValueError:
                            pass
                    for cid in _pending_handoffs_list:
                        _pending_handoffs[cid] = event.sender.get("id", "")

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
    from app.database import SessionLocal
    from app.models import Product, Order, Customer, OrderItem
    from datetime import datetime, timezone
    import re

    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return {"status": "ok"}

    staff_chat_ids = []
    if settings.TELEGRAM_ADMIN_CHAT_IDS:
        for cid in settings.TELEGRAM_ADMIN_CHAT_IDS.split(","):
            try:
                staff_chat_ids.append(int(cid.strip()))
            except ValueError:
                pass
    if settings.TELEGRAM_STAFF_CHAT_ID:
        try:
            cid = int(settings.TELEGRAM_STAFF_CHAT_ID)
            if cid not in staff_chat_ids:
                staff_chat_ids.append(cid)
        except ValueError:
            pass

    if not staff_chat_ids:
        logger.warning("No Telegram admin chat IDs configured")
        return {"status": "ok"}

    body = await request.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = sanitize_input(message.get("text", ""))
    if not chat_id or not text:
        return {"status": "ok"}

    if chat_id not in staff_chat_ids:
        logger.warning(f"Unauthorized Telegram access from chat_id: {chat_id}")
        return {"status": "ok"}

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    if text == "/start":
        menu = (
            "👋 مرحباً بك في نظام فهد!\n\n"
            "الأوامر المتاحة:\n"
            "/orders — آخر 10 طلبات اليوم\n"
            "/order <id> — تفاصيل طلب\n"
            "/confirm <id> — تأكيد طلب\n"
            "/cancel <id> — إلغاء طلب\n"
            "/products — المنتجات النشطة\n"
            "/stock <pid> <qty> — تحديث المخزون\n"
            "/addcolor <pid> <color> — إضافة لون\n"
            "/addsize <pid> <size> — إضافة مقاس\n"
            "/stats — ملخص اليوم\n\n"
            "📩 رسائلك العادية تتحول للزبون اللي مسجل في طلب التحويل."
        )
        await _send_telegram_message(chat_id, menu)
        return {"status": "ok"}

    if text == "/orders":
        db = SessionLocal()
        try:
            orders = db.query(Order).filter(Order.created_at >= today_start).order_by(Order.created_at.desc()).limit(10).all()
            if not orders:
                await _send_telegram_message(chat_id, "ماكاش طلبات اليوم.")
                return {"status": "ok"}
            lines = ["📋 آخر طلبات اليوم:"]
            for o in orders:
                c = db.query(Customer).filter(Customer.id == o.customer_id).first()
                name = c.name if c else "غير معروف"
                lines.append(f"#{o.id} — {name} — {o.total_price} دج — {o.status}")
            await _send_telegram_message(chat_id, "\n".join(lines))
        finally:
            db.close()
        return {"status": "ok"}

    m = re.match(r"^/order\s+(\d+)$", text)
    if m:
        db = SessionLocal()
        try:
            o = db.query(Order).filter(Order.id == int(m.group(1))).first()
            if not o:
                await _send_telegram_message(chat_id, "ما لقيتش الطلب.")
                return {"status": "ok"}
            c = db.query(Customer).filter(Customer.id == o.customer_id).first()
            items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
            lines = [f"🛍️ طلب #{o.id}"]
            lines.append(f"👤 {c.name if c else 'غير معروف'}")
            lines.append(f"📱 {c.phone if c else '-'}")
            lines.append(f"📍 ولاية {c.state if c else '-'}")
            lines.append(f"💰 {o.total_price} دج")
            lines.append(f"📋 الحالة: {o.status}")
            lines.append(f"📝 {o.notes or ''}")
            for item in items:
                pname = item.product.name if item.product else "غير معروف"
                lines.append(f"  • {pname} × {item.quantity} — {item.price_at_time} دج")
            lines.append(f"⏰ {o.created_at.strftime('%Y-%m-%d %H:%M')}")
            await _send_telegram_message(chat_id, "\n".join(lines))
        finally:
            db.close()
        return {"status": "ok"}

    m = re.match(r"^/confirm\s+(\d+)$", text)
    if m:
        db = SessionLocal()
        try:
            o = db.query(Order).filter(Order.id == int(m.group(1))).first()
            if not o:
                await _send_telegram_message(chat_id, "ما لقيتش الطلب.")
                return {"status": "ok"}
            o.status = "مؤكد"
            db.commit()
            await _send_telegram_message(chat_id, f"✅ تم تأكيد الطلب #{o.id}")
        finally:
            db.close()
        return {"status": "ok"}

    m = re.match(r"^/cancel\s+(\d+)$", text)
    if m:
        db = SessionLocal()
        try:
            o = db.query(Order).filter(Order.id == int(m.group(1))).first()
            if not o:
                await _send_telegram_message(chat_id, "ما لقيتش الطلب.")
                return {"status": "ok"}
            o.status = "ملغي"
            db.commit()
            await _send_telegram_message(chat_id, f"❌ تم إلغاء الطلب #{o.id}")
        finally:
            db.close()
        return {"status": "ok"}

    if text == "/products":
        db = SessionLocal()
        try:
            products = db.query(Product).filter(Product.active == True).all()
            if not products:
                await _send_telegram_message(chat_id, "ماكاش منتجات نشطة.")
                return {"status": "ok"}
            lines = ["📦 المنتجات النشطة:"]
            for p in products:
                colors = ", ".join(p.get_colors()[:3]) if p.colors else "-"
                sizes = ", ".join(p.get_sizes()[:5]) if p.sizes else "-"
                lines.append(f"#{p.id} {p.name} — {p.price} دج — مخزون: {p.stock}")
                lines.append(f"  ألوان: {colors}  |  مقاسات: {sizes}")
            await _send_telegram_message(chat_id, "\n".join(lines))
        finally:
            db.close()
        return {"status": "ok"}

    m = re.match(r"^/stock\s+(\d+)\s+(\d+)$", text)
    if m:
        db = SessionLocal()
        try:
            p = db.query(Product).filter(Product.id == int(m.group(1))).first()
            if not p:
                await _send_telegram_message(chat_id, "ما لقيتش المنتج.")
                return {"status": "ok"}
            p.stock = int(m.group(2))
            db.commit()
            await _send_telegram_message(chat_id, f"✅ تم تحديث مخزون {p.name} إلى {p.stock}")
        finally:
            db.close()
        return {"status": "ok"}

    m = re.match(r"^/addcolor\s+(\d+)\s+(.+)$", text)
    if m:
        db = SessionLocal()
        try:
            p = db.query(Product).filter(Product.id == int(m.group(1))).first()
            if not p:
                await _send_telegram_message(chat_id, "ما لقيتش المنتج.")
                return {"status": "ok"}
            colors = p.get_colors()
            colors.append(m.group(2).strip())
            p.set_colors(colors)
            db.commit()
            await _send_telegram_message(chat_id, f"✅ تم إضافة اللون. الألوان الآن: {p.colors}")
        finally:
            db.close()
        return {"status": "ok"}

    m = re.match(r"^/addsize\s+(\d+)\s+(.+)$", text)
    if m:
        db = SessionLocal()
        try:
            p = db.query(Product).filter(Product.id == int(m.group(1))).first()
            if not p:
                await _send_telegram_message(chat_id, "ما لقيتش المنتج.")
                return {"status": "ok"}
            sizes = p.get_sizes()
            sizes.append(m.group(2).strip().upper())
            p.set_sizes(sizes)
            db.commit()
            await _send_telegram_message(chat_id, f"✅ تم إضافة المقاس. المقاسات الآن: {p.sizes}")
        finally:
            db.close()
        return {"status": "ok"}

    if text == "/stats":
        db = SessionLocal()
        try:
            orders = db.query(Order).filter(Order.created_at >= today_start).all()
            total = len(orders)
            revenue = sum(o.total_price for o in orders)
            pending = sum(1 for o in orders if o.status == "pending")
            confirmed = sum(1 for o in orders if o.status in ("مؤكد", "confirmed"))
            cancelled = sum(1 for o in orders if o.status in ("ملغي", "cancelled"))
            stats = (
                f"📊 إحصائيات اليوم:\n"
                f"📋 إجمالي الطلبات: {total}\n"
                f"💰 الإيرادات: {revenue} دج\n"
                f"⏳ معلق: {pending}\n"
                f"✅ مؤكد: {confirmed}\n"
                f"❌ ملغي: {cancelled}"
            )
            await _send_telegram_message(chat_id, stats)
        finally:
            db.close()
        return {"status": "ok"}

    psid = _pending_handoffs.pop(staff_chat_ids[0], None)
    if not psid:
        await _send_telegram_message(chat_id, "ماكاش تحويل نشط دابا. استنى حتى يطلب زبون التحويل لموظف بشري.")
        return {"status": "ok"}

    await _send_messenger_message(psid, f"[موظف بشري] {text}", None)
    await _send_telegram_message(chat_id, "تم إرسال ردك للزبون ✅")
    logger.info(f"Staff reply forwarded to Facebook PSID {psid}")
    return {"status": "ok"}


async def _send_messenger_message(recipient_id: str, message: str, access_token: str = None):
    from app.config import settings as _s
    token = access_token or _s.FB_PAGE_ACCESS_TOKEN or _s.FACEBOOK_PAGE_ACCESS_TOKEN
    if not token:
        logger.error("No Facebook access token configured")
        return
    version = _s.FB_API_VERSION or "v18.0"
    url = f"https://graph.facebook.com/{version}/me/messages"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers={
            "Authorization": f"Bearer {token}"
        }, json={
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
