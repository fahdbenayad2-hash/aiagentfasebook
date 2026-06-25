from typing import List, Optional, Dict, Any, Tuple
import json
from app.services.groq_client import call_groq_json
from app.services.logging_service import logger
from app.agents.prompts.maria_system import MARIA_SYSTEM_PROMPT
from app.config import settings
from app.database import SessionLocal
from app.models import Product


def build_products_context(products: List[Product]) -> str:
    if not products:
        return "ماكاش منتجات متاحة حالياً."
    lines = []
    for p in products:
        colors = "، ".join(p.get_colors()) if p.colors else "ماكش"
        sizes = "، ".join(p.get_sizes()) if p.sizes else "ماكش"
        stock = "متوفر" if p.stock > 0 else "نفذ المخزون"
        line = f"- {p.name}: {p.price} دج ({stock}) — الألوان: {colors} — المقاسات: {sizes}"
        if p.description:
            line += f" — {p.description[:100]}"
        lines.append(line)
    return "\n".join(lines)


def build_order_context(order_draft: Optional[Dict[str, Any]]) -> str:
    if not order_draft:
        return "ما بدأتش طلبية بعد."
    parts = []
    if order_draft.get("product_name"):
        parts.append(f"المنتج: {order_draft['product_name']}")
    if order_draft.get("size"):
        parts.append(f"المقاس: {order_draft['size']}")
    if order_draft.get("color"):
        parts.append(f"اللون: {order_draft['color']}")
    if order_draft.get("quantity"):
        parts.append(f"الكمية: {order_draft['quantity']}")
    if order_draft.get("customer_name"):
        parts.append(f"الاسم: {order_draft['customer_name']}")
    if order_draft.get("phone"):
        parts.append(f"الهاتف: {order_draft['phone']}")
    if order_draft.get("wilaya"):
        parts.append(f"الولاية: {order_draft['wilaya']}")
    if order_draft.get("address"):
        parts.append(f"العنوان: {order_draft['address']}")
    if not parts:
        return "ما بدأتش طلبية بعد."
    return " | ".join(parts)


def merge_order_draft(existing: Optional[Dict[str, Any]], update: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(existing or {})
    for key in ["product_id", "product_name", "size", "color", "quantity",
                "customer_name", "phone", "wilaya", "address"]:
        if key in update and update[key] is not None:
            merged[key] = update[key]
    return merged


async def think_and_respond(
    customer_message: str,
    conversation_history: List[Dict[str, str]],
    session: Dict[str, Any],
    available_products: List[Product]
) -> Tuple[str, Dict[str, Any], str]:
    products_context = build_products_context(available_products)
    order_context = build_order_context(session.get("order_draft"))

    system_prompt = MARIA_SYSTEM_PROMPT.format(
        products_context=products_context,
        order_context=order_context
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-20:]:
        messages.append(msg)
    messages.append({"role": "user", "content": customer_message})

    try:
        raw = await call_groq_json(
            messages=messages,
            model=settings.GROQ_MODEL,
            temperature=0.7,
            max_tokens=500
        )
        data = json.loads(raw)
        response_text = data.get("message", "").strip()
        if not response_text:
            response_text = "سمعتك! كيفاش نقدر نعاونك؟ 😊"
        order_update = data.get("order_update", {})
        if not isinstance(order_update, dict):
            order_update = {}
        action = data.get("action", "CONTINUE")
        if action not in ("CONTINUE", "CREATE_ORDER", "ESCALATE", "RESET"):
            action = "CONTINUE"
        return response_text, order_update, action
    except json.JSONDecodeError:
        logger.error("Maria brain: JSON parse failed")
        return "سمعتك! كيفاش نقدر نعاونك؟ 😊", {}, "CONTINUE"
    except Exception as e:
        logger.error(f"Maria brain: {e}")
        return "سمحيلي، صابني مشكل تقني. حاولي مرة أخرى 🙏", {}, "CONTINUE"
