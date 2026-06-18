import pytest
import json
import hmac
import hashlib
from unittest.mock import patch, AsyncMock
from app.config import get_settings

settings = get_settings()


def test_facebook_verify_success(client):
    response = client.get(
        "/webhooks/facebook",
        params={
            "hub_mode": "subscribe",
            "hub_verify_token": settings.FACEBOOK_VERIFY_TOKEN,
            "hub_challenge": "123456789"
        }
    )
    assert response.status_code == 200
    assert response.text == "123456789"


def test_facebook_verify_failure(client):
    response = client.get(
        "/webhooks/facebook",
        params={
            "hub_mode": "subscribe",
            "hub_verify_token": "wrong_token",
            "hub_challenge": "123456789"
        }
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_instagram_verify_success(client):
    response = client.get(
        "/webhooks/instagram",
        params={
            "hub_mode": "subscribe",
            "hub_verify_token": settings.FACEBOOK_VERIFY_TOKEN,
            "hub_challenge": "987654321"
        }
    )
    assert response.status_code == 200
    assert response.text == "987654321"


@pytest.mark.asyncio
async def test_instagram_verify_failure(client):
    response = client.get(
        "/webhooks/instagram",
        params={
            "hub_mode": "subscribe",
            "hub_verify_token": "wrong",
            "hub_challenge": "987654321"
        }
    )
    assert response.status_code == 403


def test_facebook_webhook_invalid_signature(client):
    response = client.post(
        "/webhooks/facebook",
        json={"entry": []},
        headers={"X-Hub-Signature-256": "sha256=invalid"}
    )
    assert response.status_code == 401


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-agent-shop"
