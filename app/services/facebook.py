import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from app.config import settings
from app.services.logging_service import logger
from app.core.metrics import facebook_send_failures_total


FB_API_URL = "https://graph.facebook.com/v20.0/me/messages"


class FacebookSendClient:
    def __init__(self):
        token = settings.FB_PAGE_ACCESS_TOKEN or settings.FACEBOOK_PAGE_ACCESS_TOKEN
        self.access_token = token

    async def send_text(self, recipient_id: str, text: str) -> dict:
        if not self.access_token:
            logger.error("FB_PAGE_ACCESS_TOKEN is not set — cannot send message")
            return {"error": "missing_token"}
        try:
            return await self._send_text(recipient_id, text)
        except RetryError as e:
            logger.error(f"Failed to send Facebook message after retries: {e}")
            return {"error": "send_failed"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _send_text(self, recipient_id: str, text: str) -> dict:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text[:2000]}
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                FB_API_URL,
                params={"access_token": self.access_token},
                json=payload
            )
            if response.is_error:
                facebook_send_failures_total.labels(error_code=str(response.status_code)).inc()
                logger.error(f"Facebook Send API error: {response.status_code} {response.text[:200]}")
                response.raise_for_status()
            return response.json()

    async def send_action(self, recipient_id: str, action: str = "typing_on") -> dict:
        if not self.access_token:
            return {"error": "missing_token"}
        try:
            return await self._send_action(recipient_id, action)
        except RetryError as e:
            logger.error(f"Failed to send Facebook action after retries: {e}")
            return {"error": "send_failed"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _send_action(self, recipient_id: str, action: str = "typing_on") -> dict:
        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": action
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                FB_API_URL,
                params={"access_token": self.access_token},
                json=payload
            )
            if response.is_error:
                logger.error(f"Facebook SendAction error: {response.status_code}")
                response.raise_for_status()
            return response.json()


facebook_send = FacebookSendClient()
