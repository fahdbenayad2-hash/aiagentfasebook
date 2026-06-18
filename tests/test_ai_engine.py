import pytest
import json
from unittest.mock import patch, AsyncMock
from app.services.ai_engine import ai_engine, AIResponse


@pytest.mark.asyncio
async def test_process_message_returns_ai_response():
    products = [{"id": 1, "name": "تيشيرت", "price": 1500, "description": "تيشيرت قطني"}]
    mock_content = json.dumps({
        "intent": "greeting",
        "response": "مرحباً! كيف يمكنني مساعدتك؟",
        "extracted_data": {},
        "product_mentions": [],
        "needs_human": False,
        "state_transition": "GREETING"
    })

    with patch.object(ai_engine, "_call_groq_api", new=AsyncMock(return_value=mock_content)):
        result = await ai_engine.process_message(
            message="مرحبا",
            conversation_history=[],
            current_state="IDLE",
            context_data={},
            products=products
        )

    assert isinstance(result, AIResponse)
    assert result.intent == "greeting"
    assert result.response
    assert result.needs_human is False


@pytest.mark.asyncio
async def test_process_message_fallback_on_error():
    with patch.object(ai_engine, "_call_groq_api", new=AsyncMock(side_effect=Exception("API Error"))):
        result = await ai_engine.process_message(
            message="مرحبا",
            conversation_history=[],
            current_state="IDLE",
            context_data={},
            products=[]
        )

    assert isinstance(result, AIResponse)
    assert result.intent == "faq"
    assert "عذراً" in result.response


@pytest.mark.asyncio
async def test_process_message_empty_products():
    mock_content = json.dumps({
        "intent": "faq",
        "response": "نعم متوفر عندنا",
        "extracted_data": {},
        "product_mentions": [],
        "needs_human": False,
        "state_transition": None
    })

    with patch.object(ai_engine, "_call_groq_api", new=AsyncMock(return_value=mock_content)):
        result = await ai_engine.process_message(
            message="هل عندكم تيشيرتات؟",
            conversation_history=[],
            current_state="FAQ",
            context_data={},
            products=[]
        )

    assert result.intent == "faq"
    assert result.response
