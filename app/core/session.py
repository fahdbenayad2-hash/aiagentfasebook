import json
import time
from datetime import datetime, timezone
from typing import Optional, List
from app.models.session import ConversationState, Message
from app.models import SessionRecord
from app.config import settings


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class SessionManager:
    def __init__(self, session_factory=None):
        self._cache: dict = {}
        self._session_factory = session_factory

    def _get_db(self):
        if self._session_factory:
            return self._session_factory()
        from app.database import SessionLocal
        return SessionLocal()

    async def _load_from_db(self, sender_id: str, page_id: str) -> Optional[ConversationState]:
        import asyncio
        def _sync():
            db = self._get_db()
            try:
                rec = db.query(SessionRecord).filter(
                    SessionRecord.sender_id == sender_id,
                    SessionRecord.page_id == page_id
                ).first()
                if rec:
                    data = json.loads(rec.state_json)
                    state = ConversationState(**data)
                    if state.last_active.tzinfo is None:
                        ref = state.last_active.replace(tzinfo=timezone.utc)
                    else:
                        ref = state.last_active
                    elapsed = (datetime.now(timezone.utc) - ref).total_seconds() / 60
                    if elapsed < settings.SESSION_TTL_MINUTES:
                        return state
                return None
            finally:
                db.close()
        return await asyncio.to_thread(_sync)

    async def _save_to_db(self, state: ConversationState):
        import asyncio
        def _sync():
            db = self._get_db()
            try:
                rec = db.query(SessionRecord).filter(
                    SessionRecord.sender_id == state.sender_id,
                    SessionRecord.page_id == state.page_id
                ).first()
                if rec:
                    rec.state_json = state.model_dump_json()
                    rec.last_active = _utcnow()
                else:
                    rec = SessionRecord(
                        sender_id=state.sender_id,
                        page_id=state.page_id,
                        state_json=state.model_dump_json()
                    )
                    db.add(rec)
                db.commit()
            finally:
                db.close()
        return await asyncio.to_thread(_sync)

    async def _delete_from_db(self, sender_id: str, page_id: str):
        import asyncio
        def _sync():
            db = self._get_db()
            try:
                db.query(SessionRecord).filter(
                    SessionRecord.sender_id == sender_id,
                    SessionRecord.page_id == page_id
                ).delete()
                db.commit()
            finally:
                db.close()
        return await asyncio.to_thread(_sync)

    async def get_or_create(self, sender_id: str, page_id: str) -> ConversationState:
        cache_key = f"{sender_id}:{page_id}"
        if cache_key in self._cache:
            state = self._cache[cache_key]
            if state.last_active.tzinfo is None:
                ref = state.last_active.replace(tzinfo=timezone.utc)
            else:
                ref = state.last_active
            elapsed = (datetime.now(timezone.utc) - ref).total_seconds() / 60
            if elapsed < settings.SESSION_TTL_MINUTES:
                return state
            del self._cache[cache_key]

        state = await self._load_from_db(sender_id, page_id)
        if state:
            self._cache[cache_key] = state
            return state

        now = _utcnow()
        state = ConversationState(
            sender_id=sender_id,
            page_id=page_id,
            messages=[],
            current_intent=None,
            awaiting_tool_result=False,
            escalation_requested=False,
            language_preference="darija",
            order_id_mentioned=None,
            created_at=now,
            last_active=now
        )
        await self._save_to_db(state)
        self._cache[cache_key] = state
        return state

    async def add_message(
        self,
        sender_id: str,
        page_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None
    ) -> ConversationState:
        state = await self.get_or_create(sender_id, page_id)
        msg = Message(
            role=role,
            content=content,
            timestamp=_utcnow(),
            intent=intent
        )
        state.messages.append(msg)
        state.last_active = _utcnow()
        if len(state.messages) > settings.FAHD_MAX_MESSAGES_PER_SESSION:
            state.messages = state.messages[-settings.FAHD_MAX_MESSAGES_PER_SESSION:]
        await self._save_to_db(state)
        cache_key = f"{sender_id}:{page_id}"
        self._cache[cache_key] = state
        return state

    async def update_intent(self, sender_id: str, page_id: str, intent: str):
        state = await self.get_or_create(sender_id, page_id)
        state.current_intent = intent
        await self._save_to_db(state)

    async def set_awaiting_tool(self, sender_id: str, page_id: str, awaiting: bool):
        state = await self.get_or_create(sender_id, page_id)
        state.awaiting_tool_result = awaiting
        await self._save_to_db(state)

    async def request_escalation(self, sender_id: str, page_id: str):
        state = await self.get_or_create(sender_id, page_id)
        state.escalation_requested = True
        await self._save_to_db(state)

    async def set_language(self, sender_id: str, page_id: str, lang: str):
        state = await self.get_or_create(sender_id, page_id)
        state.language_preference = lang
        await self._save_to_db(state)

    async def save(self, sender_id: str, page_id: str, state: ConversationState):
        cache_key = f"{sender_id}:{page_id}"
        state.last_active = _utcnow()
        await self._save_to_db(state)
        self._cache[cache_key] = state

    async def delete_session(self, sender_id: str, page_id: str):
        cache_key = f"{sender_id}:{page_id}"
        self._cache.pop(cache_key, None)
        await self._delete_from_db(sender_id, page_id)


session_manager = SessionManager()
