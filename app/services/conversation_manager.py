import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Conversation, Customer, Order, OrderItem, Product
from app.schemas import AIResponse
from app.services.ai_engine import ai_engine
from app.config import get_settings
from app.services.logging_service import logger

settings = get_settings()

VALID_STATES = {
    "IDLE", "GREETING", "FAQ", "BROWSE",
    "COLLECT_NAME", "COLLECT_PHONE", "COLLECT_STATE", "COLLECT_ADDRESS",
    "CONFIRM", "HANDOFF", "ORDER_COMPLETE"
}

STATE_TRANSITIONS = {
    "IDLE": {"GREETING", "FAQ", "BROWSE", "COLLECT_NAME", "HANDOFF"},
    "GREETING": {"FAQ", "BROWSE", "COLLECT_NAME", "HANDOFF"},
    "FAQ": {"FAQ", "BROWSE", "COLLECT_NAME", "HANDOFF", "IDLE"},
    "BROWSE": {"BROWSE", "COLLECT_NAME", "FAQ", "HANDOFF", "IDLE"},
    "COLLECT_NAME": {"COLLECT_PHONE", "HANDOFF", "IDLE"},
    "COLLECT_PHONE": {"COLLECT_STATE", "COLLECT_NAME", "HANDOFF", "IDLE"},
    "COLLECT_STATE": {"COLLECT_ADDRESS", "COLLECT_PHONE", "HANDOFF", "IDLE"},
    "COLLECT_ADDRESS": {"CONFIRM", "COLLECT_STATE", "HANDOFF", "IDLE"},
    "CONFIRM": {"ORDER_COMPLETE", "COLLECT_ADDRESS", "HANDOFF", "IDLE"},
    "HANDOFF": {"IDLE", "HANDOFF"},
    "ORDER_COMPLETE": {"IDLE", "FAQ", "BROWSE"},
}

_products_cache: Dict[str, Any] = {"data": None, "timestamp": 0}


class ConversationManager:

    def get_or_create_conversation(
        self, db: Session, platform_user_id: str, platform: str
    ) -> Conversation:
        conv = db.query(Conversation).filter(
            Conversation.platform_user_id == platform_user_id,
            Conversation.platform == platform
        ).first()

        if conv:
            timeout = settings.CONVERSATION_TIMEOUT_MINUTES
            if conv.last_message_at:
                elapsed = (datetime.utcnow() - conv.last_message_at).total_seconds() / 60
                if elapsed > timeout and conv.current_state not in ("HANDOFF", "ORDER_COMPLETE"):
                    logger.info(f"Conversation {conv.id} timed out, resetting to IDLE")
                    conv.current_state = "IDLE"
                    conv.context_data = {}
                    db.commit()

        if not conv:
            conv = Conversation(
                platform_user_id=platform_user_id,
                platform=platform,
                current_state="IDLE",
                context_data={},
                messages=[]
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)

        return conv

    def get_or_create_customer(
        self, db: Session, platform_user_id: str, platform: str
    ) -> Customer:
        customer = db.query(Customer).filter(
            Customer.platform_user_id == platform_user_id,
            Customer.platform == platform
        ).first()

        if not customer:
            customer = Customer(
                platform_user_id=platform_user_id,
                platform=platform
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)

        return customer

    def _get_products(self, db: Session) -> List[Dict[str, Any]]:
        global _products_cache
        now = time.time()
        ttl = settings.PRODUCT_CACHE_TTL_SECONDS

        if _products_cache["data"] is not None and (now - _products_cache["timestamp"]) < ttl:
            return _products_cache["data"]

        products = db.query(Product).filter(Product.active == True).all()
        data = [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "description": p.description,
                "category": p.category,
                "stock": p.stock
            }
            for p in products
        ]
        _products_cache["data"] = data
        _products_cache["timestamp"] = now
        return data

    def _update_context_data(
        self, context_data: Dict[str, Any], extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        updated = dict(context_data or {})
        for key, value in extracted_data.items():
            if value and str(value).strip():
                updated[key] = value
        return updated

    def _validate_state_transition(self, current: str, new: str) -> bool:
        if new is None or new == current:
            return True
        allowed = STATE_TRANSITIONS.get(current, set())
        return new in allowed or new == current

    def _validate_phone(self, phone: str) -> bool:
        if not phone:
            return False
        digits = ''.join(c for c in phone if c.isdigit())
        return len(digits) == 10 and digits.startswith(('05', '06', '07'))

    def _validate_state_name(self, state: str) -> bool:
        if not state:
            return False
        state_clean = state.strip()
        states = [
            "أدرار", "الشلف", "الأغواط", "أم البواقي", "باتنة", "بجاية", "بسكرة", "بشار",
            "البليدة", "البويرة", "تمنراست", "تبسة", "تلمسان", "تيارت", "تيزي وزو", "الجزائر",
            "الجلفة", "جيجل", "سطيف", "سعيدة", "سكيكدة", "سيدي بلعباس", "عنابة", "قالمة",
            "قسنطينة", "المدية", "مستغانم", "المسيلة", "معسكر", "ورقلة", "وهران", "البيض",
            "إليزي", "برج بوعريريج", "بومرداس", "الطارف", "تندوف", "تيسمسيلت", "الوادي",
            "خنشلة", "سوق أهراس", "تيبازة", "ميلة", "عين الدفلى", "النعامة", "عين تموشنت",
            "غرداية", "غليزان", "تيميمون", "برج باجي مختار", "أولاد جلال", "بني عباس",
            "جانت", "المغير", "المنيعة"
        ]
        for s in states:
            if state_clean in s or s in state_clean:
                return True
        return False

    async def process_incoming_message(
        self, db: Session, platform_user_id: str, platform: str, message: str
    ) -> Dict[str, Any]:
        conv = self.get_or_create_conversation(db, platform_user_id, platform)
        customer = self.get_or_create_customer(db, platform_user_id, platform)

        if conv.customer_id is None:
            conv.customer_id = customer.id

        # ربط جديد باش SQLAlchemy يتعقب التعديل (append ما يشتغلش مع JSON column)
        conv.messages = (conv.messages or []) + [{
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        }]

        # المنتج ثابت في MARIA_SYSTEM_PROMPT — ما نحتاجش نجيبو من DB
        products = []
        history = [{"role": m["role"], "content": m["content"]} for m in conv.messages[-20:-1]]

        ai_response: AIResponse = await ai_engine.process_message(
            message=message,
            conversation_history=history,
            current_state=conv.current_state,
            context_data=conv.context_data or {},
            products=products
        )

        conv.context_data = self._update_context_data(
            conv.context_data or {},
            ai_response.extracted_data
        )

        new_state = ai_response.state_transition or conv.current_state
        if new_state and self._validate_state_transition(conv.current_state, new_state):
            conv.current_state = new_state

        response_text = ai_response.response

        # ماريا تتحقق من صحة رقم الهاتف والولاية بنفسها عبر الـ AI

        if conv.current_state == "ORDER_COMPLETE":
            order = await self._create_order_from_conversation(db, conv, customer)
            if order:
                from app.services.notification_service import notification_service
                response_text += f"\n\n📋 رقم طلبك: #{order.id}\nسنتواصل معك قريباً لتأكيد الطلب."

        if ai_response.needs_human or conv.current_state == "HANDOFF":
            conv.current_state = "HANDOFF"

        # ربط جديد لضمان حفظ الـ JSON في SQLite
        conv.messages = (conv.messages or []) + [{
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat()
        }]
        conv.last_message_at = datetime.utcnow()

        db.commit()
        db.refresh(conv)

        return {
            "response": response_text,
            "state": conv.current_state,
            "needs_human": ai_response.needs_human or conv.current_state == "HANDOFF",
            "context_data": conv.context_data,
            "conversation_id": conv.id
        }

    async def _create_order_from_conversation(
        self, db: Session, conv: Conversation, customer: Customer
    ) -> Optional[Order]:
        ctx = conv.context_data or {}

        if ctx.get("name"):
            customer.name = ctx["name"]
        if ctx.get("phone"):
            customer.phone = ctx["phone"]
        if ctx.get("state"):
            customer.state = ctx["state"]
        if ctx.get("address"):
            customer.address = ctx["address"]

        product_names = ctx.get("product_mentions", [])
        if isinstance(product_names, str):
            product_names = [product_names]
        if not product_names:
            return None

        order_items = []
        total = 0
        for pname in product_names:
            product = db.query(Product).filter(
                Product.name.ilike(f"%{pname}%"),
                Product.active == True
            ).first()
            if product:
                order_items.append((product, 1))
                total += product.price

        if not order_items:
            return None

        order = Order(
            customer_id=customer.id,
            status="pending",
            total_price=total,
            notes=f"طلب تلقائي من {conv.platform}"
        )
        db.add(order)
        db.flush()

        for product, qty in order_items:
            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                price_at_time=product.price
            )
            db.add(item)

        db.commit()
        db.refresh(order)

        try:
            from app.services.notification_service import notification_service
            await notification_service.send_order_notification({
                "order_id": order.id,
                "customer_name": customer.name or "غير معروف",
                "phone": customer.phone or "غير متوفر",
                "state": customer.state or "غير متوفر",
                "address": customer.address or "غير متوفر",
                "total": total,
                "items": [
                    {"product_name": p.name, "price": p.price, "quantity": 1}
                    for p, _ in order_items
                ]
            })
        except Exception as e:
            logger.error(f"Failed to send order notification: {e}")

        return order

    def reset_conversation(self, db: Session, platform_user_id: str, platform: str):
        conv = db.query(Conversation).filter(
            Conversation.platform_user_id == platform_user_id,
            Conversation.platform == platform
        ).first()
        if conv:
            conv.current_state = "IDLE"
            conv.context_data = {}
            conv.messages = []
            db.commit()


def invalidate_products_cache():
    global _products_cache
    _products_cache = {"data": None, "timestamp": 0}


conversation_manager = ConversationManager()
