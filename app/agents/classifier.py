from typing import Optional, List
from pydantic import BaseModel
from enum import Enum
import json
import groq

from app.agents.intents import CustomerIntent
from app.agents.prompts.classifier_system import CLASSIFIER_SYSTEM_PROMPT
from app.config import settings
from app.services.logging_service import logger
from app.core.metrics import groq_tokens_used_total


class IntentResult(BaseModel):
    intent: CustomerIntent
    confidence: float


_CLIENT = None


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)
    return _CLIENT


async def classify_intent(
    message: str,
    conversation_history: Optional[List[dict]] = None,
    language: str = "darija"
) -> Optional[IntentResult]:
    client = _get_client()
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
    ]
    if conversation_history:
        for m in conversation_history[-6:-1]:
            messages.append(m)
    messages.append({"role": "user", "content": message})

    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL or "mixtral-8x7b-32768",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=100
        )
        groq_tokens_used_total.labels(model=settings.GROQ_MODEL).inc(
            response.usage.total_tokens if response.usage else 0
        )

        text = response.choices[0].message.content
        data = json.loads(text)
        intent_str = data.get("intent", "unknown")
        confidence = float(data.get("confidence", 0.0))

        try:
            intent = CustomerIntent(intent_str)
        except ValueError:
            intent = CustomerIntent.UNKNOWN

        return IntentResult(intent=intent, confidence=confidence)

    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return None
