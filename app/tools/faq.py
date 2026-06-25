import json
import os
from typing import Optional

from app.services.cache import TTLCache


faq_cache = TTLCache(ttl=3600)


def _load_faq() -> dict:
    cached = faq_cache.get()
    if cached is not None:
        return cached
    path = os.path.join(os.path.dirname(__file__), "..", "data", "faq.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    faq_cache.set(data)
    return data


FAQ_INTENT_MAP = {
    "store_hours": "store_hours",
    "payment_methods": "payment_methods",
    "return_exchange": "return_policy",
    "delivery_delay": "delivery_info"
}


def get_faq_answer(intent, language: str = "darija") -> Optional[str]:
    faq = _load_faq()
    key = FAQ_INTENT_MAP.get(intent.value if hasattr(intent, 'value') else str(intent))
    if not key:
        return None
    entry = faq.get(key)
    if not entry:
        return None
    return entry.get(language, entry.get("darija"))
