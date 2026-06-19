from app.core.session import ConversationState, session_manager
from app.services.notification_service import notification_service
from app.services.logging_service import logger


async def escalate_to_human(sender_id: str, conversation: ConversationState, reason: str):
    await session_manager.request_escalation(sender_id, conversation.page_id)

    try:
        last_message = ""
        if conversation.messages:
            last_message = conversation.messages[-1].content

        await notification_service.send_handoff_notification({
            "customer_name": sender_id,
            "platform": "facebook",
            "last_message": last_message,
            "reason": reason
        })
        logger.info(f"Escalated {sender_id} to human, reason: {reason}")
    except Exception as e:
        logger.error(f"Failed to send escalation notification: {e}")
