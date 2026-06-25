from typing import Optional, List
from pydantic import BaseModel
from enum import Enum
import json

from app.agents.intents import CustomerIntent
from app.agents.prompts.classifier_system import CLASSIFIER_SYSTEM_PROMPT
from app.config import settings
from app.services.logging_service import logger
from app.services.groq_client import call_groq_json


class IntentResult(BaseModel):
    intent: CustomerIntent
    confidence: float


async def classify_intent(
    message: str,
    conversation_history: Optional[List[dict]] = None,
    language: str = "darija"
) -> Optional[IntentResult]:
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
    ]
    if conversation_history:
        for m in conversation_history[-6:-1]:
            messages.append(m)
    messages.append({"role": "user", "content": message})

    try:
        text = await call_groq_json(
            messages=messages,
            model=settings.GROQ_MODEL or settings.GROQ_FALLBACK_MODEL,
            temperature=0.1,
            max_tokens=100
        )
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
