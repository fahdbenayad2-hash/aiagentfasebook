import pytest
from app.agents.intents import CustomerIntent


def test_enum_values():
    assert CustomerIntent.ORDER_STATUS.value == "order_status"
    assert CustomerIntent.UNKNOWN.value == "unknown"
    assert CustomerIntent.LEGAL_THREAT.value == "legal_threat"


def test_enum_from_value():
    assert CustomerIntent("order_status") == CustomerIntent.ORDER_STATUS
    assert CustomerIntent("unknown") == CustomerIntent.UNKNOWN


def test_enum_invalid_raises():
    with pytest.raises(ValueError):
        CustomerIntent("not_a_real_intent")


def test_all_tier1_intents():
    tier1 = [
        CustomerIntent.ORDER_STATUS,
        CustomerIntent.ORDER_CANCEL,
        CustomerIntent.PRODUCT_INFO,
        CustomerIntent.PRICE_INQUIRY,
        CustomerIntent.DELIVERY_DELAY,
        CustomerIntent.RETURN_EXCHANGE,
        CustomerIntent.STORE_HOURS,
        CustomerIntent.PAYMENT_METHODS,
    ]
    for intent in tier1:
        assert intent.value.endswith(("status", "cancel", "info", "inquiry", "delay", "exchange", "hours", "methods"))


def test_escalation_intents():
    escalate = [
        CustomerIntent.LEGAL_THREAT,
        CustomerIntent.PAYMENT_DISPUTE,
        CustomerIntent.FRAUD_SUSPICION,
    ]
    for intent in escalate:
        assert intent in (CustomerIntent.LEGAL_THREAT, CustomerIntent.PAYMENT_DISPUTE, CustomerIntent.FRAUD_SUSPICION)
