from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None
    intent: Optional[str] = None


class ConversationState(BaseModel):
    sender_id: str
    page_id: str
    messages: List[Message] = []
    current_intent: Optional[str] = None
    awaiting_tool_result: bool = False
    escalation_requested: bool = False
    language_preference: str = "darija"
    order_id_mentioned: Optional[str] = None
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

    def add_message(self, role: str, content: str, intent: Optional[str] = None):
        self.messages.append(Message(role=role, content=content, intent=intent))
        if len(self.messages) > 50:
            self.messages = self.messages[-50:]

    def to_groq_messages(self) -> List[dict]:
        MAX_TURNS = 10
        recent = self.messages[-MAX_TURNS:]
        return [{"role": m.role, "content": m.content} for m in recent]
