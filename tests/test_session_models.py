import pytest
from app.models.session import ConversationState, Message


def test_conversation_state_defaults():
    state = ConversationState(sender_id="user1", page_id="page1")
    assert state.sender_id == "user1"
    assert state.page_id == "page1"
    assert state.messages == []
    assert state.current_intent is None
    assert state.escalation_requested is False


def test_conversation_state_add_message():
    state = ConversationState(sender_id="u1", page_id="p1")
    state.add_message("user", "Hello")
    assert len(state.messages) == 1
    assert state.messages[0].role == "user"
    assert state.messages[0].content == "Hello"


def test_conversation_state_history_size():
    state = ConversationState(sender_id="u1", page_id="p1")
    for i in range(60):
        state.add_message("user", f"msg {i}")
    assert len(state.messages) <= 50


def test_conversation_state_to_groq():
    state = ConversationState(sender_id="u1", page_id="p1")
    state.add_message("user", "Salam")
    state.add_message("assistant", "Wa alikom salam")
    msgs = state.to_groq_messages()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["content"] == "Wa alikom salam"


def test_message_pydantic():
    from datetime import datetime
    now = datetime.now()
    msg = Message(role="assistant", content="test reply", intent="order_status", timestamp=now)
    assert msg.role == "assistant"
    assert msg.intent == "order_status"
    assert msg.timestamp == now


def test_conversation_state_update_language():
    state = ConversationState(sender_id="u1", page_id="p1", language_preference="fr")
    assert state.language_preference == "fr"
