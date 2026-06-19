import json
import time
import aiosqlite
from datetime import datetime, timezone
from typing import Optional, List
from app.models.session import ConversationState, Message
from app.config import settings


def _utcnow():
    return datetime.now(timezone.utc)


class SessionManager:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or "data/sessions.db"
        self._cache: dict = {}

    async def _init_db(self):
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    sender_id TEXT NOT NULL,
                    page_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    last_active REAL NOT NULL,
                    PRIMARY KEY (sender_id, page_id)
                )
            """)
            await db.commit()

    def _ensure_db(self):
        import os
        if not os.path.exists(self._db_path):
            return
        if not hasattr(self, '_db_inited'):
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._init_db())
            except RuntimeError:
                pass
            self._db_inited = True

    async def get_or_create(self, sender_id: str, page_id: str) -> ConversationState:
        cache_key = f"{sender_id}:{page_id}"
        if cache_key in self._cache:
            state = self._cache[cache_key]
            elapsed = (time.time() - state.last_active.timestamp()) / 60
            if elapsed < settings.SESSION_TTL_MINUTES:
                return state
            del self._cache[cache_key]

        await self._init_db()
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT state FROM sessions WHERE sender_id = ? AND page_id = ?",
                (sender_id, page_id)
            )
            row = await cursor.fetchone()

        if row:
            data = json.loads(row["state"])
            state = ConversationState(**data)
            elapsed = (time.time() - state.last_active.timestamp()) / 60
            if elapsed < settings.SESSION_TTL_MINUTES:
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
        await self._save(state)
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
        if len(state.messages) > settings.MARIA_MAX_MESSAGES_PER_SESSION:
            state.messages = state.messages[-settings.MARIA_MAX_MESSAGES_PER_SESSION:]
        await self._save(state)
        cache_key = f"{sender_id}:{page_id}"
        self._cache[cache_key] = state
        return state

    async def update_intent(self, sender_id: str, page_id: str, intent: str):
        state = await self.get_or_create(sender_id, page_id)
        state.current_intent = intent
        await self._save(state)

    async def set_awaiting_tool(self, sender_id: str, page_id: str, awaiting: bool):
        state = await self.get_or_create(sender_id, page_id)
        state.awaiting_tool_result = awaiting
        await self._save(state)

    async def request_escalation(self, sender_id: str, page_id: str):
        state = await self.get_or_create(sender_id, page_id)
        state.escalation_requested = True
        await self._save(state)

    async def set_language(self, sender_id: str, page_id: str, lang: str):
        state = await self.get_or_create(sender_id, page_id)
        state.language_preference = lang
        await self._save(state)

    async def _save(self, state: ConversationState):
        await self._init_db()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO sessions (sender_id, page_id, state, created_at, last_active)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    state.sender_id,
                    state.page_id,
                    state.model_dump_json(),
                    state.created_at.timestamp(),
                    state.last_active.timestamp()
                )
            )
            await db.commit()

    async def delete_session(self, sender_id: str, page_id: str):
        cache_key = f"{sender_id}:{page_id}"
        self._cache.pop(cache_key, None)
        await self._init_db()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "DELETE FROM sessions WHERE sender_id = ? AND page_id = ?",
                (sender_id, page_id)
            )
            await db.commit()


session_manager = SessionManager()
