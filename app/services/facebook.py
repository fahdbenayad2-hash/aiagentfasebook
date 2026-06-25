import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from typing import Optional
from app.config import settings
from app.services.logging_service import logger
from app.core.metrics import facebook_send_failures_total


FB_API_URL = f"https://graph.facebook.com/{settings.FB_API_VERSION}/me/messages"


class FacebookSendClient:
    token_status: str = "unknown"

    def __init__(self):
        token = settings.FB_PAGE_ACCESS_TOKEN or settings.FACEBOOK_PAGE_ACCESS_TOKEN
        self.access_token = token
        self.token_status = "valid" if token else "unknown"

    async def _resolve_token(self, page_id: Optional[str] = None) -> Optional[str]:
        if page_id:
            try:
                from app.services.facebook_oauth import get_active_page_token
                db_token = await get_active_page_token(page_id)
                if db_token:
                    self.token_status = "valid"
                    return db_token
            except Exception as e:
                logger.warning(f"DB token lookup failed for page {page_id}: {e}")
        try:
            from app.services.facebook_oauth import get_active_page_token
            any_token = await get_active_page_token()
            if any_token:
                self.token_status = "valid"
                return any_token
        except Exception as e:
            logger.warning(f"DB token fallback lookup failed: {e}")
        if self.access_token:
            return self.access_token
        return None

    async def _send_telegram_alert(self):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            return
        chat_ids = []
        if settings.TELEGRAM_ADMIN_CHAT_IDS:
            for cid in settings.TELEGRAM_ADMIN_CHAT_IDS.split(","):
                try:
                    chat_ids.append(int(cid.strip()))
                except ValueError:
                    pass
        if settings.TELEGRAM_STAFF_CHAT_ID:
            try:
                cid = int(settings.TELEGRAM_STAFF_CHAT_ID)
                if cid not in chat_ids:
                    chat_ids.append(cid)
            except ValueError:
                pass
        for cid in chat_ids:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(
                        f"https://api.telegram.org/bot{token}/sendMessage",
                        json={
                            "chat_id": cid,
                            "text": (
                                "🚨 Facebook Token منتهي الصلاحية!\n"
                                "روح لـ /admin/facebook/connect لتجديد الربط"
                            )
                        }
                    )
            except Exception:
                pass

    async def send_text(self, recipient_id: str, text: str, page_id: Optional[str] = None) -> dict:
        token = await self._resolve_token(page_id)
        if not token:
            logger.error("No Facebook token available — cannot send message")
            return {"error": "missing_token"}
        try:
            result = await self._send_text(recipient_id, text, token)
            self.token_status = "valid"
            return result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                self.token_status = "expired"
                logger.critical("Facebook token expired — messages are not being delivered!")
                await self._send_telegram_alert()
            return {"error": "token_expired" if e.response.status_code == 401 else "http_error"}
        except RetryError as e:
            logger.error(f"Failed to send Facebook message after retries: {e}")
            return {"error": "send_failed"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True
    )
    async def _send_text(self, recipient_id: str, text: str, token: str) -> dict:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text[:2000]}
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                FB_API_URL,
                headers={"Authorization": f"Bearer {token}"},
                json=payload
            )
            if response.is_error:
                facebook_send_failures_total.labels(error_code=str(response.status_code)).inc()
                logger.error(f"Facebook Send API error: {response.status_code} {response.text[:200]}")
                response.raise_for_status()
            return response.json()

    async def send_action(self, recipient_id: str, action: str = "typing_on", page_id: Optional[str] = None) -> dict:
        token = await self._resolve_token(page_id)
        if not token:
            return {"error": "missing_token"}
        try:
            return await self._send_action(recipient_id, action, token)
        except RetryError as e:
            logger.error(f"Failed to send Facebook action after retries: {e}")
            return {"error": "send_failed"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _send_action(self, recipient_id: str, action: str, token: str) -> dict:
        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": action
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                FB_API_URL,
                headers={"Authorization": f"Bearer {token}"},
                json=payload
            )
            if response.is_error:
                logger.error(f"Facebook SendAction error: {response.status_code}")
                response.raise_for_status()
            return response.json()


facebook_send = FacebookSendClient()
