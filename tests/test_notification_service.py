import pytest
import respx
from httpx import Response
from app.services.notification_service import NotificationService


@pytest.fixture
def svc():
    s = NotificationService()
    s.bot_token = "test:bot"
    s.chat_id = "-100test"
    s.base_url = "https://api.telegram.org/bottest:bot"
    return s


@pytest.fixture
def svc_no_token():
    s = NotificationService()
    s.bot_token = ""
    s.base_url = ""
    return s


@respx.mock
@pytest.mark.asyncio
async def test_send_order_notification_success(svc):
    route = respx.post("https://api.telegram.org/bottest:bot/sendMessage").mock(
        return_value=Response(200, json={"ok": True})
    )
    result = await svc.send_order_notification({
        "order_id": 42,
        "customer_name": "زبون",
        "phone": "0555123456",
        "state": "الجزائر",
        "address": "عنوان",
        "total": 1500,
        "items": [{"product_name": "قندورة", "price": 1500, "quantity": 1}]
    })
    assert result is True
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_send_order_notification_failure(svc):
    respx.post("https://api.telegram.org/bottest:bot/sendMessage").mock(
        return_value=Response(500, json={"ok": False})
    )
    result = await svc.send_order_notification({
        "order_id": 42,
        "customer_name": "زبون",
        "phone": "0555123456",
        "state": "الجزائر",
        "items": []
    })
    assert result is False


@pytest.mark.asyncio
async def test_send_order_notification_no_token(svc_no_token):
    result = await svc_no_token.send_order_notification({"order_id": 1})
    assert result is False


@respx.mock
@pytest.mark.asyncio
async def test_send_handoff_notification_success(svc):
    route = respx.post("https://api.telegram.org/bottest:bot/sendMessage").mock(
        return_value=Response(200, json={"ok": True})
    )
    result = await svc.send_handoff_notification({
        "customer_name": "زبون",
        "platform": "facebook",
        "last_message": "مساعدة"
    })
    assert result is True
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_send_handoff_notification_failure(svc):
    respx.post("https://api.telegram.org/bottest:bot/sendMessage").mock(
        return_value=Response(500)
    )
    result = await svc.send_handoff_notification({
        "customer_name": "زبون",
        "platform": "facebook",
        "last_message": "مساعدة"
    })
    assert result is False


@pytest.mark.asyncio
async def test_send_handoff_notification_no_token(svc_no_token):
    result = await svc_no_token.send_handoff_notification({"customer_name": "test"})
    assert result is False
