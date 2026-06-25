from typing import Optional
import httpx
from app.config import get_settings
from app.services.logging_service import logger

settings = get_settings()


class NotificationService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_STAFF_CHAT_ID
        if self.bot_token:
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        else:
            self.base_url = ""
            logger.error("TELEGRAM_BOT_TOKEN is empty — notifications disabled")

    async def send_order_notification(self, order_data: dict) -> bool:
        if not self.bot_token:
            logger.error("Telegram not configured, skipping order notification")
            return False
        try:
            message = self._format_order_message(order_data)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send order notification: {e}")
            return False

    async def send_handoff_notification(self, conversation_data: dict) -> bool:
        if not self.bot_token:
            logger.error("Telegram not configured, skipping handoff notification")
            return False
        try:
            n = "\n"
            message = "".join([
                "\U0001f6a8 <b>\u0637\u0644\u0628 \u062a\u062d\u0648\u064a\u0644 \u0644\u0645\u0648\u0638\u0641 \u0628\u0634\u0631\u064a</b>",
                n, "\u2501" * 14, n,
                "\U0001f464 \u0627\u0644\u0639\u0645\u064a\u0644: ", conversation_data.get('customer_name', '\u063a\u064a\u0631 \u0645\u0639\u0631\u0648\u0641'),
                n, "\U0001f4f1 \u0627\u0644\u0645\u0646\u0635\u0629: ", conversation_data.get('platform', '\u063a\u064a\u0631 \u0645\u0639\u0631\u0648\u0641'),
                n, "\U0001f4ac \u0622\u062e\u0631 \u0631\u0633\u0627\u0644\u0629: ", str(conversation_data.get('last_message', '\u0644\u0627 \u064a\u0648\u062c\u062f'))[:100],
                n, "\U0001f4e9 \u0631\u062f \u0639\u0644\u064a\u0647 \u0628\u0643\u062a\u0627\u0628\u0629 \u0627\u0644\u0631\u062f \u0647\u0646\u0627"
            ])
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send handoff notification: {e}")
            return False

    def _format_order_message(self, order_data: dict) -> str:
        n = "\n"
        items_text = n.join([
            f"\u2022 {item['product_name']} - {item['price']} \u062f\u062c \u00d7 {item['quantity']}"
            for item in order_data.get("items", [])
        ])
        x = "\u2501" * 14
        return "".join([
            "\U0001f6d2 <b>\u0637\u0644\u0628 \u062c\u062f\u064a\u062f!</b>",
            n, x, n,
            "\U0001f464 \u0627\u0644\u0639\u0645\u064a\u0644: ", order_data.get('customer_name', '\u063a\u064a\u0631 \u0645\u0639\u0631\u0648\u0641'),
            n, "\U0001f4f1 \u0627\u0644\u0647\u0627\u062a\u0641: ", order_data.get('phone', '\u063a\u064a\u0631 \u0645\u062a\u0648\u0641\u0631'),
            n, "\U0001f4cd \u0627\u0644\u0648\u0644\u0627\u064a\u0629: ", order_data.get('state', '\u063a\u064a\u0631 \u0645\u062a\u0648\u0641\u0631'),
            n, "\U0001f3e0 \u0627\u0644\u0639\u0646\u0648\u0627\u0646: ", order_data.get('address', '\u063a\u064a\u0631 \u0645\u062a\u0648\u0641\u0631'),
            n, x, n,
            "\U0001f4e6 \u0627\u0644\u0645\u0646\u062a\u062c\u0627\u062a:", n, items_text,
            n, x, n,
            "\U0001f4b0 \u0627\u0644\u0625\u062c\u0645\u0627\u0644\u064a: ", str(order_data.get('total', 0)), " \u062f\u062c",
            n, "\U0001f194 \u0631\u0642\u0645 \u0627\u0644\u0637\u0644\u0628: #", str(order_data.get('order_id', 'N/A'))
        ])


notification_service = NotificationService()


async def send_telegram_notification(message: str, chat_id: Optional[str] = None) -> bool:
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return False
    if not chat_id:
        chat_id = settings.TELEGRAM_STAFF_CHAT_ID
    if not chat_id:
        from app.database import SessionLocal
        from app.models import User
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_chat_id.isnot(None)).first()
            if user:
                chat_id = user.telegram_chat_id
        finally:
            db.close()
    if not chat_id:
        logger.error("No Telegram chat_id configured anywhere")
        return False
    logger.info(f"Sending Telegram notification to chat_id={chat_id}")
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            response = await client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
            )
            if response.status_code != 200:
                logger.error(f"Telegram send failed: {response.status_code} {response.text}")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"send_telegram_notification failed: {e}")
        return False
