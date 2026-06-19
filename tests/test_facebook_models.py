import pytest
from app.models.facebook import WebhookPayload, MessagingEvent, WebhookEntry, MessagePayload, PostbackPayload


@pytest.fixture
def sample_payload():
    return WebhookPayload(
        object="page",
        entry=[WebhookEntry(
            id="12345",
            time=1234567890,
            messaging=[MessagingEvent(
                sender={"id": "user1"},
                recipient={"id": "page1"},
                timestamp=1234567890,
                message=MessagePayload(mid="mid1", text="Hello"),
                postback=None
            )]
        )]
    )


def test_webhook_payload_parses(sample_payload):
    assert sample_payload.object == "page"
    assert len(sample_payload.entry) == 1
    assert sample_payload.entry[0].messaging[0].sender["id"] == "user1"


def test_messaging_event_creates():
    event = MessagingEvent(
        sender={"id": "test"},
        recipient={"id": "page"},
        timestamp=123,
        message=MessagePayload(mid="m1", text="hi"),
        postback=None
    )
    assert event.sender["id"] == "test"
    assert event.message.text == "hi"


def test_messaging_event_no_message():
    event = MessagingEvent(
        sender={"id": "test"},
        recipient={"id": "page"},
        timestamp=123,
        message=None,
        postback=PostbackPayload(payload="START", title="Start")
    )
    assert event.postback.payload == "START"
    assert event.message is None


def test_extract_events(sample_payload):
    events = sample_payload.extract_events()
    assert len(events) == 1
    assert events[0].sender["id"] == "user1"
    assert events[0].message_id == "mid1"


def test_webhook_payload_empty_entry():
    payload = WebhookPayload(object="page", entry=[])
    assert payload.entry == []
    assert payload.extract_events() == []


def test_webhook_entry_empty_messaging():
    entry = WebhookEntry(id="123", messaging=[])
    assert entry.messaging == []
