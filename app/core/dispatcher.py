from app.models.facebook import MessagingEvent
from app.models.session import ConversationState
from app.core.session import session_manager
from app.core.security import detect_prompt_injection, rate_limiter
from app.services.facebook import facebook_send
from app.agents.classifier import classify_intent
from app.agents.maria import generate_reply
from app.agents.intents import CustomerIntent
from app.services.logging_service import logger
from app.core.metrics import (
    messages_received_total,
    intents_classified_total,
    escalations_total,
    tool_calls_total
)
from app.tools.order_lookup import lookup_order
from app.tools.faq import get_faq_answer
from app.tools.catalog import search_catalog
from app.tools.escalation import escalate_to_human


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
            await facebook_send.send_text(recipient_id=sender_id, text=text)
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

    intent_result = await classify_intent(
        message=message_text,
        conversation_history=state.to_groq_messages(),
        language=state.language_preference
    )

    if intent_result:
        confidence_bucket = "high" if intent_result.confidence >= 0.8 else "medium" if intent_result.confidence >= 0.5 else "low"
        intents_classified_total.labels(
            intent=intent_result.intent.value if hasattr(intent_result.intent, 'value') else str(intent_result.intent),
            confidence_bucket=confidence_bucket
        ).inc()
        await session_manager.update_intent(sender_id, page_id, intent_result.intent.value)

    intent = intent_result.intent if intent_result else CustomerIntent.UNKNOWN
    tool_result = None

    if intent == CustomerIntent.ORDER_STATUS:
        tool_calls_total.labels(tool_name="order_lookup", status="attempt").inc()
        order_id = state.order_id_mentioned or _extract_order_id(message_text)
        if order_id:
            tool_result = await lookup_order(order_id, sender_id)
            if tool_result.get("error"):
                tool_calls_total.labels(tool_name="order_lookup", status="error").inc()
            else:
                tool_calls_total.labels(tool_name="order_lookup", status="success").inc()

    elif intent == CustomerIntent.ORDER_CANCEL:
        tool_calls_total.labels(tool_name="order_lookup", status="attempt").inc()
        order_id = state.order_id_mentioned or _extract_order_id(message_text)
        if order_id:
            tool_result = await lookup_order(order_id, sender_id)
            if tool_result and not tool_result.get("error"):
                tool_calls_total.labels(tool_name="order_lookup", status="success").inc()

    elif intent in (CustomerIntent.STORE_HOURS, CustomerIntent.PAYMENT_METHODS, CustomerIntent.RETURN_EXCHANGE):
        tool_calls_total.labels(tool_name="faq", status="attempt").inc()
        tool_result = get_faq_answer(intent, state.language_preference)
        tool_calls_total.labels(tool_name="faq", status="success").inc()

    elif intent in (CustomerIntent.PRODUCT_INFO, CustomerIntent.PRICE_INQUIRY):
        tool_calls_total.labels(tool_name="catalog", status="attempt").inc()
        tool_result = await search_catalog(message_text)
        tool_calls_total.labels(tool_name="catalog", status="success").inc()

    if intent in (CustomerIntent.LEGAL_THREAT, CustomerIntent.PAYMENT_DISPUTE, CustomerIntent.FRAUD_SUSPICION):
        tool_calls_total.labels(tool_name="escalation", status="attempt").inc()
        await escalate_to_human(sender_id, state, reason=f"Intent: {intent.value}")
        await session_manager.request_escalation(sender_id, page_id)
        tool_calls_total.labels(tool_name="escalation", status="success").inc()
        escalations_total.labels(reason=intent.value).inc()
        await safe_send("نوصلك للمسؤول دابا، صبر شويا 😊")
        return

    if intent in (CustomerIntent.UNKNOWN, CustomerIntent.OUT_OF_SCOPE):
        reply = "سمعتك! كيفاش نقدر نعاونك؟ 😊"
        await safe_send(reply)
        await session_manager.add_message(sender_id, page_id, "assistant", reply, intent="handoff")
        return

    reply = await generate_reply(
        message=message_text,
        state=state,
        intent=intent,
        tool_result=tool_result
    )

    await safe_send(reply)
    await session_manager.add_message(
        sender_id, page_id, "assistant", reply,
        intent=intent.value if hasattr(intent, 'value') else str(intent)
    )


def _extract_order_id(text: str) -> str:
    import re
    match = re.search(r"#?(\d{3,8})", text)
    if match:
        return match.group(1)
    match = re.search(r"(?:commande|order|طلب)\s*[#: ]?\s*(\d{3,8})", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""
