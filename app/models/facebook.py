from pydantic import BaseModel
from typing import List, Optional, Any


class Profile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_pic: Optional[str] = None


class MessagePayload(BaseModel):
    mid: Optional[str] = None
    text: Optional[str] = None
    is_echo: bool = False
    quick_reply: Optional[dict] = None
    attachments: Optional[List[dict]] = None


class PostbackPayload(BaseModel):
    title: Optional[str] = None
    payload: Optional[str] = None
    referral: Optional[dict] = None


class MessagingEvent(BaseModel):
    sender: dict
    recipient: dict
    timestamp: Optional[int] = None
    message: Optional[MessagePayload] = None
    postback: Optional[PostbackPayload] = None
    message_id: Optional[str] = None


class WebhookEntry(BaseModel):
    id: str
    time: Optional[int] = None
    messaging: List[MessagingEvent] = []


class WebhookPayload(BaseModel):
    object: str
    entry: List[WebhookEntry] = []

    def extract_events(self) -> List[MessagingEvent]:
        events = []
        for entry in self.entry:
            for event in entry.messaging:
                if event.message:
                    event.message_id = event.message.mid
                events.append(event)
        return events
