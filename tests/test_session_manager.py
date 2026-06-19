import pytest
import pytest_asyncio
import tempfile
import os
from app.core.session import SessionManager


@pytest_asyncio.fixture
async def manager():
    tmp = tempfile.mktemp(suffix=".db")
    m = SessionManager(db_path=tmp)
    return m


@pytest.mark.asyncio
async def test_get_or_create_new(manager):
    state = await manager.get_or_create("user1", "page1")
    assert state.sender_id == "user1"
    assert state.page_id == "page1"
    assert state.messages == []


@pytest.mark.asyncio
async def test_get_or_create_existing(manager):
    state1 = await manager.get_or_create("user2", "page1")
    state2 = await manager.get_or_create("user2", "page1")
    assert state2.sender_id == "user2"
    assert state2.page_id == "page1"


@pytest.mark.asyncio
async def test_add_message(manager):
    await manager.get_or_create("user3", "page1")
    await manager.add_message("user3", "page1", "user", "Hello")
    state = await manager.get_or_create("user3", "page1")
    assert len(state.messages) == 1
    assert state.messages[0].content == "Hello"
    assert state.messages[0].role == "user"


@pytest.mark.asyncio
async def test_add_multiple_messages(manager):
    await manager.get_or_create("user4", "page1")
    await manager.add_message("user4", "page1", "user", "Hi")
    await manager.add_message("user4", "page1", "assistant", "Hello")
    state = await manager.get_or_create("user4", "page1")
    assert len(state.messages) == 2


@pytest.mark.asyncio
async def test_update_intent(manager):
    await manager.get_or_create("user5", "page1")
    await manager.add_message("user5", "page1", "user", "win order 123?")
    await manager.update_intent("user5", "page1", "order_status")
    state = await manager.get_or_create("user5", "page1")
    assert state.current_intent == "order_status"


@pytest.mark.asyncio
async def test_request_escalation(manager):
    await manager.get_or_create("user6", "page1")
    await manager.request_escalation("user6", "page1")
    state = await manager.get_or_create("user6", "page1")
    assert state.escalation_requested is True


@pytest.mark.asyncio
async def test_add_message_with_intent(manager):
    await manager.get_or_create("user7", "page1")
    await manager.add_message("user7", "page1", "assistant", "Reply", intent="order_status")
    state = await manager.get_or_create("user7", "page1")
    assert state.messages[-1].intent == "order_status"
