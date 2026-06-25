import json
import pytest
from unittest.mock import patch, AsyncMock
from app.services.ai_engine import ai_engine
from app.services.conversation_manager import conversation_manager
from app.models import Customer, Product


def _seed_test_data(db_session):
    customer = Customer(platform_user_id="test_psid", platform="facebook", name="سارة")
    db_session.add(customer)
    db_session.flush()

    products = [
        Product(id=1, name="قندورة سيتان", price=3200, category="قنادر", stock=10, description="قندورة سيتان فاخرة", complementary_product_ids="2"),
        Product(id=2, name="حزام جلد", price=800, category="إكسسوارات", stock=15, description="حزام جلد ناعم"),
        Product(id=3, name="بيجامة قطيفة", price=2800, category="بيجامات", stock=5, description="بيجامة قطيفة 3 قطع"),
    ]
    for p in products:
        db_session.add(p)
    db_session.commit()
    return customer


def _make_json_response(intent="faq", response_text="نعم"):
    return {
        "content": json.dumps({
            "intent": intent,
            "response": response_text,
            "extracted_data": {},
            "product_mentions": [],
            "needs_human": False,
            "state_transition": None
        })
    }


def _make_tool_call(name: str, args: dict, call_id="call_1"):
    return {
        "tool_calls": [{
            "id": call_id,
            "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)}
        }]
    }


def _make_handoff_json_response():
    return {
        "content": json.dumps({
            "intent": "handoff",
            "response": "تم تحويلك إلى الموظف البشري ✅",
            "extracted_data": {},
            "product_mentions": [],
            "needs_human": True,
            "state_transition": "HANDOFF"
        })
    }


class TestToolCalling:

    @pytest.mark.asyncio
    async def test_product_inquiry_calls_get_available_products(self, db_session):
        _seed_test_data(db_session)
        called_tools = []

        async def mock_call(messages):
            has_tool = any(m.get("role") == "tool" for m in messages)
            if not has_tool:
                tc = _make_tool_call("get_available_products", {"category": "قنادر"})
                called_tools.append("get_available_products")
                return tc
            return _make_json_response("browse", "عندنا قنادر متنوعة 😊")

        with patch.object(ai_engine, "_call_groq_with_tools", new=AsyncMock(side_effect=mock_call)):
            result = await conversation_manager.process_incoming_message(
                db=db_session,
                platform_user_id="test_psid",
                platform="facebook",
                message="شو عندكم من قنادر؟"
            )

        assert "get_available_products" in called_tools

    @pytest.mark.asyncio
    async def test_size_fabric_query_calls_get_product_details(self, db_session):
        _seed_test_data(db_session)
        called_tools = []

        async def mock_call(messages):
            has_tool = any(m.get("role") == "tool" for m in messages)
            if not has_tool:
                tc = _make_tool_call("get_product_details", {"product_identifier": "قندورة"})
                called_tools.append("get_product_details")
                return tc
            return _make_json_response("faq", "هاذ القندورة مقاساتها S M L XL 😊")

        with patch.object(ai_engine, "_call_groq_with_tools", new=AsyncMock(side_effect=mock_call)):
            result = await conversation_manager.process_incoming_message(
                db=db_session,
                platform_user_id="test_psid",
                platform="facebook",
                message="واش عندكم مقاس L؟ قماشو إيش؟"
            )

        assert "get_product_details" in called_tools

    @pytest.mark.asyncio
    async def test_availability_check_calls_get_product_details(self, db_session):
        _seed_test_data(db_session)
        called_tools = []

        async def mock_call(messages):
            has_tool = any(m.get("role") == "tool" for m in messages)
            if not has_tool:
                tc = _make_tool_call("get_product_details", {"product_identifier": "1"})
                called_tools.append("get_product_details")
                return tc
            return _make_json_response("faq", "ايوه المنتج موجود عندنا 😊")

        with patch.object(ai_engine, "_call_groq_with_tools", new=AsyncMock(side_effect=mock_call)):
            result = await conversation_manager.process_incoming_message(
                db=db_session,
                platform_user_id="test_psid",
                platform="facebook",
                message="هذا المنتج موجود؟"
            )

        assert "get_product_details" in called_tools

    @pytest.mark.asyncio
    async def test_discount_request_no_escalation(self, db_session):
        _seed_test_data(db_session)
        called_tools = []

        async def mock_call(messages):
            has_tool = any(m.get("role") == "tool" for m in messages)
            if not has_tool:
                return _make_json_response("faq", "الأسعار ثابتة يا أختي 🌸 نقدر نعاونك في حاجة أخرى؟")
            return _make_json_response("faq", "الأسعار ثابتة")

        with patch.object(ai_engine, "_call_groq_with_tools", new=AsyncMock(side_effect=mock_call)):
            result = await conversation_manager.process_incoming_message(
                db=db_session,
                platform_user_id="test_psid",
                platform="facebook",
                message="ما تعطينيش تخفيض؟"
            )

        assert result["needs_human"] is False

    @pytest.mark.asyncio
    async def test_upsell_calls_get_complementary_products(self, db_session):
        _seed_test_data(db_session)
        called_tools = []

        async def mock_call(messages):
            has_tool = any(m.get("role") == "tool" for m in messages)
            if not has_tool:
                tc = _make_tool_call("get_complementary_products", {"current_product_id": "1"})
                called_tools.append("get_complementary_products")
                return tc
            return _make_json_response("collect_info", "تمام! عندنا حزام جلد يناسبها 😊 شنو اسمك؟")

        with patch.object(ai_engine, "_call_groq_with_tools", new=AsyncMock(side_effect=mock_call)):
            result = await conversation_manager.process_incoming_message(
                db=db_session,
                platform_user_id="test_psid",
                platform="facebook",
                message="تمام، كيفاش نطلبها؟"
            )

        assert "get_complementary_products" in called_tools

    @pytest.mark.asyncio
    async def test_escalation_triggers_handoff(self, db_session):
        _seed_test_data(db_session)
        called_tools = []

        async def mock_call(messages):
            has_tool = any(m.get("role") == "tool" for m in messages)
            if not has_tool:
                return _make_handoff_json_response()
            return _make_handoff_json_response()

        with patch.object(ai_engine, "_call_groq_with_tools", new=AsyncMock(side_effect=mock_call)):
            result = await conversation_manager.process_incoming_message(
                db=db_session,
                platform_user_id="test_psid",
                platform="facebook",
                message="حابة نحكي مع شخص"
            )

        assert result["needs_human"] is True
