from app.database import SessionLocal
from app.models import ConversationLog
from app.services.logging_service import logger


async def log_conversation(
    sender_id: str,
    customer_id: int = None,
    message_count: int = 0,
    completed_order: bool = False,
    escalated: bool = False,
    product_name: str = None
):
    db = SessionLocal()
    try:
        log = ConversationLog(
            sender_id=sender_id,
            customer_id=customer_id,
            message_count=message_count,
            completed_order=completed_order,
            escalated=escalated,
            product_name=product_name
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log conversation: {e}")
    finally:
        db.close()
