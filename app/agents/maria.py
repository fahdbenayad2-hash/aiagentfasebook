from typing import Optional, Any
import json

from app.agents.intents import CustomerIntent
from app.agents.prompts.maria_system import MARIA_SYSTEM_PROMPT
from app.models.session import ConversationState
from app.config import settings
from app.services.logging_service import logger
from app.services.groq_client import call_groq_json


TOOL_DESCRIPTIONS = {
    "order_lookup": "Check order status by order ID",
    "faq": "Store hours, payment methods, return policy",
    "catalog": "Search products by name or category",
    "escalation": "Transfer to human agent",
}


async def generate_reply(
    message: str,
    state: ConversationState,
    intent: CustomerIntent,
    tool_result: Optional[Any] = None
) -> str:
    available_tools = []
    if intent in (CustomerIntent.ORDER_STATUS, CustomerIntent.ORDER_CANCEL):
        available_tools.append(f"order_lookup: {TOOL_DESCRIPTIONS['order_lookup']}")
    if intent in (CustomerIntent.STORE_HOURS, CustomerIntent.PAYMENT_METHODS, CustomerIntent.RETURN_EXCHANGE):
        available_tools.append(f"faq: {TOOL_DESCRIPTIONS['faq']}")
    if intent in (CustomerIntent.PRODUCT_INFO, CustomerIntent.PRICE_INQUIRY):
        available_tools.append(f"catalog: {TOOL_DESCRIPTIONS['catalog']}")

    context_vars = {
        "conversation_history": json.dumps(state.to_groq_messages()[-10:], ensure_ascii=False),
        "intent": intent.value,
        "available_tools": ", ".join(available_tools) if available_tools else "none"
    }

    system_prompt = MARIA_SYSTEM_PROMPT.format(**context_vars)

    messages = [{"role": "system", "content": system_prompt}]

    if tool_result:
        try:
            serialized = json.dumps(tool_result, ensure_ascii=False)
        except (TypeError, ValueError):
            if hasattr(tool_result, "to_dict"):
                serialized = json.dumps(tool_result.to_dict(), ensure_ascii=False)
            elif isinstance(tool_result, list):
                serialized = json.dumps(
                    [t.to_dict() if hasattr(t, "to_dict") else str(t) for t in tool_result],
                    ensure_ascii=False
                )
            else:
                serialized = str(tool_result)
        messages.append({
            "role": "system",
            "content": f"Tool result: {serialized}"
        })

    messages.extend(state.to_groq_messages()[-5:])
    messages.append({"role": "user", "content": message})

    try:
        text = await call_groq_json(
            messages=messages,
            model=settings.GROQ_MODEL or settings.GROQ_FALLBACK_MODEL,
            temperature=0.7,
            max_tokens=300
        )
        data = json.loads(text)
        reply = data.get("message") or data.get("text") or data.get("reply") or text

        if isinstance(reply, dict):
            reply = reply.get("text", json.dumps(reply, ensure_ascii=False))

        return str(reply)[:2000]

    except json.JSONDecodeError:
        return "سمعتك! كيفاش نقدر نعاونك؟ 😊"
    except Exception as e:
        logger.error(f"Maria reply generation failed: {e}")
        return "سمحيلي، صابني مشكل تقني. حاولي مرة أخرى 🙏"
