import pytest
import json
import hmac
import hashlib
from unittest.mock import patch, AsyncMock


def _hmac_signature(body: bytes, secret: str = "test") -> str:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={expected}"


def _payload(text="Hello", sender="u1"):
    return json.dumps({"object": "page", "entry": [
        {"id": "page1", "messaging": [
            {"sender": {"id": sender}, "recipient": {"id": "p1"},
             "message": {"text": text, "mid": "mid.1"}}
        ]}
    ]})


def test_webhook_verify_get(client):
    response = client.get(
        "/webhooks/facebook",
        params={"hub.mode": "subscribe", "hub.verify_token": "test_verify", "hub.challenge": "ch123"}
    )
    assert response.status_code == 200
    assert response.text == "ch123"


def test_webhook_verify_get_bad_token(client):
    response = client.get(
        "/webhooks/facebook",
        params={"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "ch123"}
    )
    assert response.status_code == 403


def test_webhook_post_valid_hmac(client):
    body = _payload().encode()
    sig = _hmac_signature(body)

    with patch("app.core.dispatcher.handle_event", new=AsyncMock()) as mock_he:

        response = client.post(
            "/webhooks/facebook",
            content=body,
            headers={"X-Hub-Signature-256": sig, "Content-Type": "application/json"}
        )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_he.assert_called_once()


def test_webhook_post_invalid_hmac(client):
    body = _payload().encode()

    response = client.post(
        "/webhooks/facebook",
        content=body,
        headers={"X-Hub-Signature-256": "sha256=invalid", "Content-Type": "application/json"}
    )
    assert response.status_code == 401


def test_webhook_post_empty_messaging(client):
    body = json.dumps({"object": "page", "entry": [{"id": "page1", "messaging": []}]}).encode()
    sig = _hmac_signature(body)

    response = client.post(
        "/webhooks/facebook",
        content=body,
        headers={"X-Hub-Signature-256": sig, "Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_post_with_escalation(client):
    body = _payload(text="موظف").encode()
    sig = _hmac_signature(body)

    with patch("app.core.dispatcher.handle_event", new=AsyncMock()) as mock_he:

        response = client.post(
            "/webhooks/facebook",
            content=body,
            headers={"X-Hub-Signature-256": sig, "Content-Type": "application/json"}
        )
    assert response.status_code == 200
    mock_he.assert_called_once()
