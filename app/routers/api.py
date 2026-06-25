import csv
import io
import json
import math
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Customer, Product, Order, OrderItem, Conversation, ConversationLog, FacebookConnection
from app.routers.auth import get_current_user
from app.config import settings
from app.services.logging_service import logger
from app.services.conversation_manager import invalidate_products_cache
from app.utils.arabic import normalize_arabic

router = APIRouter(prefix="/api", tags=["api"])


#
# ─── DASHBOARD STATS ─────────────────────────────────────
#

@router.get("/dashboard/stats")
async def dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today_start = datetime.now(timezone.utc).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)

    convs_today = db.query(Conversation).filter(Conversation.last_message_at >= today_start).count()
    convs_yesterday = db.query(Conversation).filter(
        Conversation.last_message_at >= yesterday_start,
        Conversation.last_message_at < today_start
    ).count()

    orders_today = db.query(Order).filter(Order.created_at >= today_start).count()
    orders_yesterday = db.query(Order).filter(
        Order.created_at >= yesterday_start,
        Order.created_at < today_start
    ).count()

    total_convs = db.query(Conversation).count()
    completed_orders = db.query(ConversationLog).filter(ConversationLog.completed_order == True).count()
    close_rate = round(completed_orders / total_convs * 100, 1) if total_convs > 0 else 0

    def delta_str(current: int, previous: int) -> str:
        if previous == 0:
            return f"+{current}"
        diff = current - previous
        if diff >= 0:
            return f"+{diff}"
        return str(diff)

    return {
        "conversations_today": convs_today,
        "orders_new": orders_today,
        "close_rate": close_rate,
        "credits_remaining": current_user.credits,
        "conv_delta": delta_str(convs_today, convs_yesterday),
        "order_delta": delta_str(orders_today, orders_yesterday),
        "rate_delta": f"{close_rate}%",
    }


#
# ─── CONVERSATIONS ─────────────────────────────────────
#

def _conv_status(conv: Conversation) -> str:
    if conv.current_state == "ORDER_COMPLETE":
        return "مغلق"
    if conv.manual_mode:
        return "يدوي"
    if conv.current_state == "HANDOFF":
        return "يدوي"
    return "مريا"


def _time_ago(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = now - dt.replace(tzinfo=None) if dt.tzinfo else now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "لحظات"
    minutes = seconds // 60
    if minutes < 60:
        return f"منذ {minutes} د"
    hours = minutes // 60
    if hours < 24:
        return f"منذ {hours} س"
    days = hours // 24
    if days < 30:
        return f"منذ {days} ي"
    return dt.strftime("%Y-%m-%d")


def _last_message_text(conv: Conversation) -> str:
    msgs = conv.messages or []
    for m in reversed(msgs):
        if isinstance(m, dict) and m.get("content"):
            return m["content"][:120]
    return ""


def _conv_to_row(conv: Conversation) -> dict:
    cname = conv.customer.name if conv.customer else conv.platform_user_id[-8:]
    return {
        "id": conv.id,
        "customer_name": cname,
        "last_message": _last_message_text(conv),
        "time_ago": _time_ago(conv.last_message_at),
        "status": _conv_status(conv),
        "unread": 0,
    }


@router.get("/conversations")
async def list_conversations(
    limit: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Conversation).order_by(Conversation.last_message_at.desc().nullslast())
    if limit:
        q = q.limit(limit)
    convs = q.all()
    return [_conv_to_row(c) for c in convs]


@router.get("/conversations/{conv_id}")
async def get_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    row = _conv_to_row(conv)
    row["manual"] = conv.manual_mode
    return row


@router.get("/conversations/{conv_id}/messages")
async def get_conversation_messages(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = conv.messages or []
    return [
        {
            "role": m.get("role", "user"),
            "content": m.get("content", ""),
            "timestamp": m.get("timestamp", ""),
        }
        for m in msgs
    ]


class ModeUpdate(BaseModel):
    manual: bool


@router.patch("/conversations/{conv_id}/mode")
async def toggle_manual_mode(
    conv_id: int,
    body: ModeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.manual_mode = body.manual
    db.commit()
    return {"success": True}


class ManualReply(BaseModel):
    message: str


@router.post("/conversations/{conv_id}/manual-reply")
async def send_manual_reply(
    conv_id: int,
    body: ManualReply,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    response_text = body.message.strip()
    if not response_text:
        raise HTTPException(status_code=400, detail="Message is empty")

    conv.messages = (conv.messages or []) + [
        {"role": "assistant", "content": response_text, "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}
    ]
    conv.last_message_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()

    try:
        from app.services.facebook import facebook_send
        page_id = conv.context_data.get("page_id") if isinstance(conv.context_data, dict) else None
        await facebook_send.send_text(
            recipient_id=conv.platform_user_id,
            text=response_text,
            page_id=page_id,
        )
    except Exception as e:
        logger.error(f"Failed to send manual reply via Facebook: {e}")

    return {"success": True}


#
# ─── ORDERS ─────────────────────────────────────
#

def _order_to_row(order: Order) -> dict:
    c = order.customer
    product_name = ""
    size = ""
    for item in order.items:
        if item.product:
            product_name = item.product.name
            break
    return {
        "id": order.id,
        "customer": c.name if c else "غير معروف",
        "wilaya": c.state if c and c.state else "غير محدد",
        "product": product_name,
        "size": size,
        "total": order.total_price,
        "status": order.status,
        "date": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else "",
    }


STATUS_MAP = {
    "معلق": "pending",
    "pending": "pending",
    "مؤكد": "confirmed",
    "confirmed": "confirmed",
    "في التوصيل": "shipped",
    "shipped": "shipped",
    "مسلّم": "delivered",
    "delivered": "delivered",
    "ملغي": "cancelled",
    "cancelled": "cancelled",
}


@router.get("/orders")
async def list_orders(
    limit: Optional[int] = Query(None),
    wilaya: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Order).join(Customer, Order.customer_id == Customer.id, isouter=True)
    if wilaya:
        q = q.filter(Customer.state.ilike(f"%{wilaya}%"))
    if status:
        db_status = STATUS_MAP.get(status, status)
        q = q.filter(Order.status == db_status)
    if from_date:
        try:
            fd = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=None)
            q = q.filter(Order.created_at >= fd)
        except ValueError:
            pass
    if to_date:
        try:
            td = datetime.strptime(to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=None)
            q = q.filter(Order.created_at <= td)
        except ValueError:
            pass
    q = q.order_by(Order.created_at.desc())
    if limit:
        q = q.limit(limit)
    orders = q.all()
    return [_order_to_row(o) for o in orders]


class OrderStatusUpdate(BaseModel):
    status: str


@router.patch("/orders/{order_id}")
async def update_order(
    order_id: int,
    body: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db_status = STATUS_MAP.get(body.status, body.status)
    order.status = db_status
    db.commit()
    return {"success": True}


#
# ─── FACEBOOK CONNECTIONS ─────────────────────────────────────
#

@router.get("/facebook/connections")
async def get_facebook_connections(
    current_user: User = Depends(get_current_user),
):
    from app.services.facebook_oauth import get_active_connections, decrypt_token, mask_token
    connections = await get_active_connections()
    return {
        "connections": [
            {
                "name": conn.page_name,
                "id": conn.page_id,
                "token_preview": mask_token(decrypt_token(conn.page_access_token_encrypted)),
                "connected_at": conn.connected_at.isoformat() if conn.connected_at else None,
                "is_active": conn.is_active,
            }
            for conn in connections
        ]
    }


#
# ─── CUSTOMERS ─────────────────────────────────────
#

@router.get("/customers")
async def list_customers(
    limit: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Customer).order_by(Customer.created_at.desc())
    if search:
        q = q.filter(Customer.name.ilike(f"%{search}%"))
    if limit:
        q = q.limit(limit)
    customers = q.all()
    return [
        {
            "id": c.id,
            "name": c.name or "غير معروف",
            "phone": c.phone or "",
            "state": c.state or "",
            "platform": c.platform,
            "orders_count": len(c.orders) if hasattr(c, "orders") else 0,
            "created_at": c.created_at.strftime("%Y-%m-%d") if c.created_at else "",
        }
        for c in customers
    ]


#
# ─── PRODUCTS ─────────────────────────────────────
#

@router.get("/products")
async def list_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "description": p.description,
            "category": p.category,
            "stock": p.stock,
            "active": p.active,
            "colors": p.get_colors(),
            "sizes": p.get_sizes(),
            "image_url": p.image_url,
        }
        for p in products
    ]


class ProductAvailableUpdate(BaseModel):
    available: bool


class ProductCreate(BaseModel):
    name: str
    price: int
    stock: int = 0
    category: str = ""
    description: str = ""
    colors: str = ""
    sizes: str = ""


@router.post("/products")
async def create_product(
    body: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = Product(
        name=body.name.strip(),
        price=body.price,
        stock=body.stock,
        category=body.category.strip() or None,
        description=body.description.strip(),
    )
    if body.colors.strip():
        product.set_colors([c.strip() for c in body.colors.split(",") if c.strip()])
    if body.sizes.strip():
        product.set_sizes([s.strip() for s in body.sizes.split(",") if s.strip()])
    db.add(product)
    db.commit()
    invalidate_products_cache()
    return {"id": product.id, "name": product.name}


@router.patch("/products/{product_id}")
async def toggle_product_availability(
    product_id: int,
    body: ProductAvailableUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.active = body.available
    db.commit()
    invalidate_products_cache()
    return {"success": True}


@router.post("/products/upload")
async def upload_products(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = await file.read()
    added = []

    if file.filename and file.filename.endswith(".csv"):
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            product = Product(
                name=row.get("name", "").strip(),
                price=int(row.get("price", 0)),
                description=row.get("description", "").strip() or None,
                category=row.get("category", "").strip() or None,
                stock=int(row.get("stock", 0)),
                active=row.get("active", "1").strip() in ("1", "true", "True", "yes"),
            )
            if row.get("colors"):
                product.set_colors([c.strip() for c in row["colors"].split(",")])
            if row.get("sizes"):
                product.set_sizes([s.strip() for s in row["sizes"].split(",")])
            db.add(product)
            db.flush()
            added.append({"id": product.id, "name": product.name})
    else:
        try:
            data = json.loads(content.decode("utf-8"))
            if isinstance(data, dict):
                data = [data]
            for row in data:
                product = Product(
                    name=row.get("name", "").strip(),
                    price=int(row.get("price", 0)),
                    description=row.get("description", "").strip() or None,
                    category=row.get("category", "").strip() or None,
                    stock=int(row.get("stock", 0)),
                    active=row.get("active", True),
                )
                if row.get("colors"):
                    clist = row["colors"] if isinstance(row["colors"], list) else [c.strip() for c in row["colors"].split(",")]
                    product.set_colors(clist)
                if row.get("sizes"):
                    slist = row["sizes"] if isinstance(row["sizes"], list) else [s.strip() for s in row["sizes"].split(",")]
                    product.set_sizes(slist)
                db.add(product)
                db.flush()
                added.append({"id": product.id, "name": product.name})
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise HTTPException(status_code=400, detail="Invalid file format. Use CSV or JSON.")

    db.commit()
    invalidate_products_cache()
    return added


#
# ─── SETTINGS / NOTIFICATIONS ─────────────────────────────────────
#

@router.get("/settings/notifications")
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
):
    return {
        "phone": current_user.notification_phone or "",
        "new_order": current_user.notify_new_order if current_user.notify_new_order is not None else True,
        "handoff": current_user.notify_handoff if current_user.notify_handoff is not None else True,
    }


class NotificationSettingsUpdate(BaseModel):
    phone: str = ""
    new_order: bool = True
    handoff: bool = True


@router.put("/settings/notifications")
async def update_notification_settings(
    body: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    user.notification_phone = body.phone.strip() or None
    user.notify_new_order = body.new_order
    user.notify_handoff = body.handoff
    db.commit()
    return {"success": True}


#
# ─── PAYMENTS (SATIM stub) ─────────────────────────────────────
#

class SatimRequest(BaseModel):
    amount: int
    pack_id: str
    user_id: int


@router.post("/payments/initiate-satim")
async def initiate_satim_payment(
    body: SatimRequest,
    current_user: User = Depends(get_current_user),
):
    from app.services.logging_service import logger
    logger.info(f"SATIM payment requested: amount={body.amount}, pack={body.pack_id}, user={body.user_id}")
    return {
        "payment_url": f"/payment/pending?amount={body.amount}&pack={body.pack_id}&user={body.user_id}",
        "transaction_id": f"TXN{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "status": "pending",
    }


#
# ─── DEMO CHAT ─────────────────────────────────────
#

class DemoChatRequest(BaseModel):
    message: str
    session_id: str = ""
    history: list = []


@router.post("/demo/chat")
async def demo_chat(body: DemoChatRequest):
    from app.agents.maria_brain import think_and_respond
    from app.database import SessionLocal
    from app.models import Product

    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.active == True).all()
    except Exception:
        products = []
    finally:
        db.close()

    history = body.history or []
    groq_history = [{"role": m["role"], "content": m["content"]} for m in history[-20:]]

    try:
        response_text, _, _ = await think_and_respond(
            customer_message=body.message,
            conversation_history=groq_history,
            session={"order_draft": None},
            available_products=products,
        )
    except Exception as e:
        logger.error(f"Demo chat error: {e}")
        response_text = "عذراً، حدث خطأ. حاول مرة أخرى"

    return {"reply": response_text}


#
# ─── WEBSOCKET ─────────────────────────────────────
#

@router.websocket("/ws/conversations/{conv_id}")
async def conversation_websocket(websocket: WebSocket, conv_id: int):
    await websocket.accept()
    token = websocket.query_params.get("token", "")
    from app.routers.auth import _decode_token
    from app.database import SessionLocal

    user_id = _decode_token(token)
    if not user_id:
        await websocket.send_json({"error": "Unauthorized"})
        await websocket.close()
        return

    db = SessionLocal()
    try:
        conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
        if not conv:
            await websocket.send_json({"error": "Conversation not found"})
            await websocket.close()
            return
    finally:
        db.close()

    last_count = 0
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                db2 = SessionLocal()
                try:
                    conv2 = db2.query(Conversation).filter(Conversation.id == conv_id).first()
                    if conv2:
                        msgs = conv2.messages or []
                        if len(msgs) > last_count:
                            new_msgs = msgs[last_count:]
                            for m in new_msgs:
                                await websocket.send_json({
                                    "role": m.get("role", "user"),
                                    "content": m.get("content", ""),
                                    "timestamp": m.get("timestamp", ""),
                                })
                            last_count = len(msgs)
                finally:
                    db2.close()
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
