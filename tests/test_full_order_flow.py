"""Test 5: Full order conversation simulation.
10 messages flowing naturally, maria_brain handling all responses."""

import pytest
import json
from unittest.mock import patch, AsyncMock
from app.agents.maria_brain import think_and_respond, merge_order_draft


MOCK_RESPONSES = {
    "سلام": json.dumps({
        "message": "وعليكم السلام! 😊 كيفاش نعاونك؟",
        "order_update": {},
        "action": "CONTINUE"
    }),
    "عندكم بجامة نسائية؟": json.dumps({
        "message": "ايوه عندنا بجامة نسائية ب 3200 دج. الألوان: أبيض، أسود، وردي. المقاسات: M، L، XL. واش تحبي؟",
        "order_update": {"product_name": "بجامة نسائية"},
        "action": "CONTINUE"
    }),
    "نحبها بيضاء": json.dumps({
        "message": "تمام! اخترتي اللون الأبيض 😊 واش المقاس لي تحبي؟",
        "order_update": {"color": "أبيض"},
        "action": "CONTINUE"
    }),
    "مقاس L": json.dumps({
        "message": "مقاس L، زينة! شحال قطعة تحبي؟",
        "order_update": {"size": "L"},
        "action": "CONTINUE"
    }),
    "واحدة بصح": json.dumps({
        "message": "حاجة وحدة 😊 شكون نكتب في الطلبية؟ اعطيني اسمك الكامل",
        "order_update": {"quantity": 1},
        "action": "CONTINUE"
    }),
    "أنا سارة بن علي": json.dumps({
        "message": "سارة بن علي، مرحبا بيك 😊 واش رقم هاتفك؟",
        "order_update": {"customer_name": "سارة بن علي"},
        "action": "CONTINUE"
    }),
    "0661234567": json.dumps({
        "message": "رقمك 0661234567، مليح! من وين نتي؟ (رقم الولاية 1-58)",
        "order_update": {"phone": "0661234567"},
        "action": "CONTINUE"
    }),
    "16": json.dumps({
        "message": "ولاية 16 — الجزائر العاصمة 🏠 شنو عنوانك بالتفصيل؟",
        "order_update": {"wilaya": 16},
        "action": "CONTINUE"
    }),
    "حي السلام، بئر خادم، الجزائر": json.dumps({
        "message": "عنوانك حي السلام، بئر خادم، الجزائر. نأكدي طلبيتك:\n🛍️ بجامة نسائية — أبيض — L × 1\n💰 3200 دج\n👤 سارة بن علي\n📱 0661234567\n📍 ولاية 16\n\nواش تأكدي؟",
        "order_update": {"address": "حي السلام، بئر خادم، الجزائر"},
        "action": "CONTINUE"
    }),
    "نعم": json.dumps({
        "message": "✅ تم تسجيل طلبيتك! شكراً على ثقتك 😊",
        "order_update": {},
        "action": "CREATE_ORDER"
    }),
}


@pytest.mark.asyncio
async def test_full_order_conversation():
    messages = [
        "سلام",                         # 0: greeting
        "عندكم بجامة نسائية؟",           # 1: product inquiry
        "نحبها بيضاء",                   # 2: color
        "مقاس L",                        # 3: size
        "واحدة بصح",                     # 4: quantity
        "أنا سارة بن علي",               # 5: name
        "0661234567",                    # 6: phone
        "16",                             # 7: wilaya
        "حي السلام، بئر خادم، الجزائر",  # 8: address
        "نعم",                           # 9: confirm → CREATE_ORDER
    ]

    session = {"order_draft": None}
    history = []
    final_action = None

    for i, msg in enumerate(messages):
        mock_json = MOCK_RESPONSES.get(msg)
        assert mock_json, f"Turn {i}: missing mock for '{msg}'"

        with patch("app.agents.maria_brain.call_groq_json", new=AsyncMock(return_value=mock_json)):
            response_text, order_update, action = await think_and_respond(
                customer_message=msg,
                conversation_history=history,
                session=session,
                available_products=[]
            )

        assert response_text, f"Turn {i}: empty response"
        assert action in ("CONTINUE", "CREATE_ORDER", "RESET", "ESCALATE"), f"Turn {i}: invalid action {action}"

        merged = merge_order_draft(session["order_draft"], order_update)
        session["order_draft"] = merged
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": response_text})

        if action == "CREATE_ORDER":
            final_action = action
            break

    # Last action must be CREATE_ORDER
    assert final_action == "CREATE_ORDER", "Order was never finalized"

    # Order draft should be complete at the point of creation
    draft = session["order_draft"]
    assert draft["product_name"] == "بجامة نسائية"
    assert draft["color"] == "أبيض"
    assert draft["size"] == "L"
    assert draft["quantity"] == 1
    assert draft["customer_name"] == "سارة بن علي"
    assert draft["phone"] == "0661234567"
    assert draft["wilaya"] == 16
    assert draft["address"] == "حي السلام، بئر خادم، الجزائر"

    # History should contain all 10 exchanges (20 messages)
    assert len(history) == len(messages) * 2, f"Expected {len(messages)*2} history entries, got {len(history)}"
