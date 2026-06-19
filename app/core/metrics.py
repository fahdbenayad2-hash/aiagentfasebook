from prometheus_client import Counter, Histogram
import time
from functools import wraps


messages_received_total = Counter(
    "maria_messages_received_total",
    "Messages received",
    ["page_id"]
)

intents_classified_total = Counter(
    "maria_intents_classified_total",
    "Intents classified",
    ["intent", "confidence_bucket"]
)

groq_tokens_used_total = Counter(
    "maria_groq_tokens_used_total",
    "Groq tokens used",
    ["model"]
)

escalations_total = Counter(
    "maria_escalations_total",
    "Escalations to human",
    ["reason"]
)

response_latency_seconds = Histogram(
    "maria_response_latency_seconds",
    "Response latency",
    buckets=[0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0]
)

session_duration_seconds = Histogram(
    "maria_session_duration_seconds",
    "Session duration",
    buckets=[60, 300, 600, 1800, 3600, 7200]
)

tool_calls_total = Counter(
    "maria_tool_calls_total",
    "Tool calls",
    ["tool_name", "status"]
)

facebook_send_failures_total = Counter(
    "maria_facebook_send_failures_total",
    "Facebook Send API failures",
    ["error_code"]
)


def track_latency():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                elapsed = time.time() - start
                response_latency_seconds.observe(elapsed)
        return wrapper
    return decorator
