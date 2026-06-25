from typing import List, Dict, Optional
import httpx
from app.config import settings
from app.core.metrics import groq_tokens_used_total
from app.services.logging_service import logger


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


async def call_groq_json(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 300
) -> str:
    model = model or settings.GROQ_MODEL
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "response_format": {"type": "json_object"},
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        response.raise_for_status()
        data = response.json()
        groq_tokens_used_total.labels(model=model).inc(
            data.get("usage", {}).get("total_tokens", 0)
        )
        return data["choices"][0]["message"]["content"]
