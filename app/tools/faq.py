import json
import os
from typing import Optional


_FAQ_CACHE = None


def _load_faq() -> dict:
    global _FAQ_CACHE
    if _FAQ_CACHE is not None:
        return _FAQ_CACHE
    path = os.path.join(os.path.dirname(__file__), "..", "data", "faq.json")
    try:
        with open(path, encoding="utf-8") as f:
            _FAQ_CACHE = json.load(f)
    except FileNotFoundError:
        _FAQ_CACHE = {}
    return _FAQ_CACHE


FAQ_INTENT_MAP = {
    "store_hours": "store_hours",
    "payment_methods": "payment_methods",
    "return_exchange": "return_policy",
    "delivery_delay": "delivery_info",
    "store_hours": "store_hours"
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
