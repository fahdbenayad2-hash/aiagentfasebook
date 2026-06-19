import hmac
import hashlib
import re
from typing import Dict, Any
from app.config import settings
from app.services.logging_service import logger


INJECTION_PATTERNS = re.compile(
    r"(?:ignore\s+(?:all\s+)?previous\s+instructions|"
    r"you\s+are\s+now|"
    r"system\s+prompt|"
    r"\bDAN\b|"
    r"jailbreak|"
    r"you\s+must\s+ignore|"
    r"new\s+instructions|"
    r"override\s+(?:all|previous|system))",
    re.IGNORECASE
)


def verify_fb_signature(payload: bytes, signature: str) -> bool:
    if not signature:
        return False
    secret = settings.FB_APP_SECRET or settings.FACEBOOK_APP_SECRET
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    result = hmac.compare_digest(f"sha256={expected}", signature)
    if not result:
        logger.warning("Facebook signature verification failed")
    return result


def detect_prompt_injection(text: str) -> bool:
    if INJECTION_PATTERNS.search(text):
        logger.warning(f"Prompt injection attempt detected: {text[:80]}")
        return True
    return False


def scrub_pii(text: str) -> str:
    phone_pattern = re.compile(r"(?:\+213|0)(?:5|6|7)\d{8}")
    text = phone_pattern.sub("[PHONE]", text)
    name_pattern = re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b")
    text = name_pattern.sub("[NAME]", text)
    address_keywords = re.compile(
        r"\b(?:rue|avenue|boulevard|cité|représ|bled|ville|commune|district)\s+\w+",
        re.IGNORECASE
    )
    text = address_keywords.sub("[ADDRESS]", text)
    return text


class RateLimiter:
    def __init__(self):
        self._buckets: Dict[str, list] = {}

    def check(self, key: str, max_per_minute: int = 10) -> bool:
        import time
        now = time.time()
        window = 60.0
        if key not in self._buckets:
            self._buckets[key] = []
        self._buckets[key] = [t for t in self._buckets[key] if now - t < window]
        if len(self._buckets[key]) >= max_per_minute:
            return False
        self._buckets[key].append(now)
        return True


rate_limiter = RateLimiter()
