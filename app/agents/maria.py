from typing import Optional, Any
import json
import groq

from app.agents.intents import CustomerIntent
from app.agents.prompts.maria_system import MARIA_SYSTEM_PROMPT
from app.models.session import ConversationState
from app.config import settings
from app.services.logging_service import logger
from app.core.metrics import groq_tokens_used_total


_CLIENT = None


TOOL_DESCRIPTIONS = {
    "order_lookup": "Check order status by order ID",
    "faq": "Store hours, payment methods, return policy",
    "catalog": "Search products by name or category",
    "escalation": "Transfer to human agent",
}


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)
    return _CLIENT


async def generate_reply(
    message: str,
    state: ConversationState,
    intent: CustomerIntent,
    tool_result: Optional[Any] = None
) -> str:
    client = _get_client()

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
        messages.append({
            "role": "system",
            "content": f"Tool result: {json.dumps(tool_result, ensure_ascii=False)}"
        })

    messages.extend(state.to_groq_messages()[-5:])
    messages.append({"role": "user", "content": message})

    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL or "mixtral-8x7b-32768",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=300
        )
        groq_tokens_used_total.labels(model=settings.GROQ_MODEL).inc(
            response.usage.total_tokens if response.usage else 0
        )

        text = response.choices[0].message.content
        data = json.loads(text)
        reply = data.get("message") or data.get("text") or data.get("reply") or text

        if isinstance(reply, dict):
            reply = reply.get("text", json.dumps(reply, ensure_ascii=False))

        return str(reply)[:2000]

    except json.JSONDecodeError:
        return "سمعتك! كيفاش نقدر نعاونك؟ 😊"
    except Exception as e:
        logger.error(f"Maria reply generation failed: {e}")
        return "عفواً، واجهت مشكلة تقنية. جرب مرة أخرى 🙏"
