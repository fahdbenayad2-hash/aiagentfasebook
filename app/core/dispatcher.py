from app.config import settings
from app.models.facebook import MessagingEvent
from app.models.session import ConversationState, OrderDraft
from app.core.session import session_manager
from app.core.security import detect_prompt_injection, rate_limiter
from app.services.facebook import facebook_send
from app.services.logging_service import logger
from app.core.metrics import (
    messages_received_total,
    escalations_total,
)
from app.agents.maria_brain import think_and_respond, merge_order_draft
from app.tools.order_flow import create_order
from app.services.learning import log_conversation
from app.database import SessionLocal
from app.models import Product


async def handle_event(event: MessagingEvent):
    sender_id = event.sender.get("id", "")
    page_id = event.recipient.get("id", "")
    message_text = ""
    message_type = "text"
    quick_reply_payload = None

    if event.message:
        message_text = (event.message.text or "").strip()
        if event.message.quick_reply:
            quick_reply_payload = event.message.quick_reply.get("payload")
            message_type = "quick_reply"
        if event.message.attachments:
            message_type = "attachment"
    elif event.postback:
        message_text = event.postback.payload or event.postback.title or ""
        message_type = "postback"

    if not message_text and message_type != "attachment":
        return

    messages_received_total.labels(page_id=page_id).inc()

    async def safe_send(text: str):
        try:
            await facebook_send.send_text(recipient_id=sender_id, text=text, page_id=page_id)
        except Exception as e:
            logger.error(f"Failed to send message to {sender_id}: {e}")

    if not rate_limiter.check(sender_id):
        logger.info(f"Rate limited sender {sender_id}")
        await safe_send("ساعليك شويا، راهي كثرت علينا. صبر شوية وحاول مرة أخرى 😊")
        return

    state = await session_manager.get_or_create(sender_id, page_id)

    if state.escalation_requested:
        import time
        cooldown = settings.MARIA_COOLDOWN_AFTER_ESCALATION_MINUTES * 60
        last_active = state.last_active
        if last_active is not None:
            elapsed = time.time() - last_active.timestamp()
            if elapsed < cooldown:
                await safe_send("طلبك تم تحويله للمسؤول. راهو يقراه وإن شاء الله يرد عليك قريباً 😊")
                return

    is_injection = detect_prompt_injection(message_text)
    if is_injection:
        logger.warning(f"Prompt injection blocked for {sender_id}")
        await safe_send("فهمتك! كيفاش نقدر نعاونك؟ 😊")
        return

    await session_manager.add_message(sender_id, page_id, "user", message_text)
    state = await session_manager.get_or_create(sender_id, page_id)

    db = None
    try:
        db = SessionLocal()
        available_products = db.query(Product).filter(Product.active == True).all()
    except Exception:
        available_products = []
    finally:
        if db:
            db.close()

    session_dict = {
        "order_draft": state.order_draft.model_dump() if state.order_draft else None
    }
    history = [{"role": m.role, "content": m.content} for m in state.messages[-20:]]

    response_text, order_update, action = await think_and_respond(
        customer_message=message_text,
        conversation_history=history,
        session=session_dict,
        available_products=available_products
    )

    merged = merge_order_draft(session_dict["order_draft"], order_update)
    state.order_draft = OrderDraft(**merged) if merged else None

    if action == "CREATE_ORDER":
        if state.order_draft:
            order = await create_order(sender_id, state.order_draft)
            await log_conversation(
                sender_id=sender_id,
                customer_id=order.customer_id,
                message_count=len(state.messages),
                completed_order=True,
                product_name=state.order_draft.product_name
            )
            state.order_draft = None

    elif action == "ESCALATE":
        from app.tools.escalation import escalate_to_human
        await escalate_to_human(sender_id, state, reason="Customer requested human agent")
        await session_manager.request_escalation(sender_id, page_id)
        escalations_total.labels(reason="customer_requested").inc()
        await log_conversation(
            sender_id=sender_id,
            message_count=len(state.messages),
            escalated=True
        )

    elif action == "RESET":
        state.order_draft = None

    await safe_send(response_text)
    await session_manager.add_message(sender_id, page_id, "assistant", response_text)


def _extract_order_id(text: str) -> str:
    import re
    match = re.search(r"(?:#|commande|order|طلب)\s*[#: ]?\s*(\d{3,8})", text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"(?<!\d)(\d{4,8})(?!\d)", text)
    if match:
        return match.group(1)
    return ""
