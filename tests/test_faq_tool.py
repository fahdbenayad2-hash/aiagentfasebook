import pytest
from app.tools.faq import get_faq_answer
from app.agents.intents import CustomerIntent


def test_get_faq_answer_store_hours():
    answer = get_faq_answer(CustomerIntent.STORE_HOURS, "darija")
    assert answer is not None
    assert isinstance(answer, str)


def test_get_faq_answer_payment_methods():
    answer = get_faq_answer(CustomerIntent.PAYMENT_METHODS, "darija")
    assert answer is not None


def test_get_faq_answer_return_exchange():
    answer = get_faq_answer(CustomerIntent.RETURN_EXCHANGE, "darija")
    assert answer is not None


def test_get_faq_answer_unknown_intent():
    answer = get_faq_answer(CustomerIntent.UNKNOWN, "darija")
    assert answer is None


def test_get_faq_answer_french():
    answer = get_faq_answer(CustomerIntent.STORE_HOURS, "fr")
    assert answer is not None


def test_get_faq_answer_fallback_to_darija():
    answer = get_faq_answer(CustomerIntent.STORE_HOURS, "ar")
    assert answer is not None
