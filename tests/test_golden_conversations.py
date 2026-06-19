import json
import os
import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GOLDEN_PATH = FIXTURES_DIR / "golden_conversations.json"

REQUIRES_GROQ = os.environ.get("GROQ_API_KEY", "").startswith("gsk_")
DO_SKIP = not REQUIRES_GROQ or os.environ.get("GROQ_API_KEY") == "gsk_test"


@pytest.fixture(scope="session")
def golden_conversations():
    with open(GOLDEN_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.skipif(DO_SKIP, reason="Requires real Groq API key")
@pytest.mark.asyncio
async def test_golden_intent_classification(golden_conversations):
    from app.agents.classifier import classify_intent

    errors = []
    for conv in golden_conversations:
        last_user_msg = ""
        for msg in conv["messages"]:
            if msg["role"] == "user":
                last_user_msg = msg["content"]

        result = await classify_intent(last_user_msg)
        if result is None:
            errors.append(f"{conv['id']}: classifier returned None")
            continue

        expected = conv["expected_intent"]
        if result.intent.value != expected:
            errors.append(
                f"{conv['id']}: expected={expected}, got={result.intent.value} "
                f"(confidence={result.confidence:.2f})"
            )

    assert not errors, f"Classification failures:\n" + "\n".join(errors[:5])


@pytest.mark.skipif(DO_SKIP, reason="Requires real Groq API key")
@pytest.mark.asyncio
async def test_golden_reply_generation(golden_conversations):
    from app.agents.classifier import classify_intent
    from app.agents.maria import generate_reply
    from app.models.session import ConversationState
    from app.agents.intents import CustomerIntent

    errors = []
    for conv in golden_conversations:
        last_user_msg = ""
        conv_history = []
        for msg in conv["messages"]:
            if msg["role"] == "user":
                last_user_msg = msg["content"]
            conv_history.append(msg)

        state = ConversationState(sender_id="golden_test", page_id="page1")
        for msg in conv_history:
            state.add_message(msg["role"], msg["content"])

        intent_result = await classify_intent(last_user_msg, conversation_history=conv_history)
        if intent_result is None:
            errors.append(f"{conv['id']}: classifier returned None, skipping reply")
            continue

        reply = await generate_reply(
            message=last_user_msg,
            state=state,
            intent=intent_result.intent,
            tool_result=None
        )

        if not reply or len(reply) < 5:
            errors.append(f"{conv['id']}: reply too short: '{reply}'")
            continue

        if intent_result.intent in (
            CustomerIntent.LEGAL_THREAT,
            CustomerIntent.PAYMENT_DISPUTE,
            CustomerIntent.FRAUD_SUSPICION,
        ):
            disallowed = ["رقم", "order #", "#SF", "commande #"]
            if any(d in reply for d in disallowed):
                errors.append(f"{conv['id']}: escalation intent should not fabricate order numbers")

    assert not errors, f"Reply failures:\n" + "\n".join(errors[:5])


@pytest.mark.skipif(DO_SKIP, reason="Requires real Groq API key")
def test_all_intents_represented(golden_conversations):
    from app.agents.intents import CustomerIntent

    covered = set(c["expected_intent"] for c in golden_conversations)
    all_intents = set(i.value for i in CustomerIntent)

    uncovered = all_intents - covered
    assert not uncovered, f"Intents missing from golden dataset: {uncovered}"
