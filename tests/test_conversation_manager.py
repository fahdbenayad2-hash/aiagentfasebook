import pytest
import json
from unittest.mock import patch, AsyncMock
from app.services.conversation_manager import conversation_manager
from app.models import Product, Customer, Conversation
from app.schemas import AIResponse


@pytest.mark.asyncio
async def test_get_or_create_conversation_new(db_session):
    conv = conversation_manager.get_or_create_conversation(
        db_session, "test_user_1", "facebook"
    )
    assert conv is not None
    assert conv.platform_user_id == "test_user_1"
    assert conv.platform == "facebook"
    assert conv.current_state == "IDLE"


@pytest.mark.asyncio
async def test_get_or_create_conversation_existing(db_session):
    conv1 = conversation_manager.get_or_create_conversation(
        db_session, "test_user_2", "facebook"
    )
    conv2 = conversation_manager.get_or_create_conversation(
        db_session, "test_user_2", "facebook"
    )
    assert conv1.id == conv2.id


@pytest.mark.asyncio
async def test_get_or_create_customer(db_session):
    customer = conversation_manager.get_or_create_customer(
        db_session, "cust_1", "instagram"
    )
    assert customer is not None
    assert customer.platform_user_id == "cust_1"
    assert customer.platform == "instagram"


@pytest.mark.asyncio
async def test_validate_phone():
    assert conversation_manager._validate_phone("0555123456") is True
    assert conversation_manager._validate_phone("0655123456") is True
    assert conversation_manager._validate_phone("0755123456") is True
    assert conversation_manager._validate_phone("055512345") is False
    assert conversation_manager._validate_phone("05551234567") is False
    assert conversation_manager._validate_phone("") is False
    assert conversation_manager._validate_phone("abc") is False


@pytest.mark.asyncio
async def test_validate_state_name():
    assert conversation_manager._validate_state_name("الجزائر") is True
    assert conversation_manager._validate_state_name("وهران") is True
    assert conversation_manager._validate_state_name("باريس") is False
    assert conversation_manager._validate_state_name("") is False


@pytest.mark.asyncio
async def test_process_incoming_message(db_session):
    mock_response = AIResponse(
        intent="greeting",
        response="مرحباً! كيف يمكنني مساعدتك؟",
        extracted_data={},
        product_mentions=[],
        needs_human=False,
        state_transition="GREETING"
    )

    with patch.object(conversation_manager, "_get_products", return_value=[]):
        with patch("app.services.conversation_manager.ai_engine.process_message",
                   new=AsyncMock(return_value=mock_response)):
            result = await conversation_manager.process_incoming_message(
                db_session, "test_user_3", "facebook", "مرحبا"
            )

    assert result["response"] == "مرحباً! كيف يمكنني مساعدتك؟"
    assert result["state"] == "GREETING"
    assert result["needs_human"] is False
    assert result["conversation_id"] is not None


@pytest.mark.asyncio
async def test_reset_conversation(db_session):
    conv = conversation_manager.get_or_create_conversation(
        db_session, "reset_user", "facebook"
    )
    conv.current_state = "COLLECT_NAME"
    conv.context_data = {"name": "أحمد"}
    db_session.commit()

    conversation_manager.reset_conversation(db_session, "reset_user", "facebook")

    conv = conversation_manager.get_or_create_conversation(
        db_session, "reset_user", "facebook"
    )
    assert conv.current_state == "IDLE"
    assert conv.context_data == {}
    assert conv.messages == []
