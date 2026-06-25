import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

VALID_TOOLS = {
    "get_product_details",
    "get_available_products",
    "update_customer_profile",
    "get_complementary_products",
}

VALID_PROFILE_FIELDS = {"preferred_size", "fabric_preference", "last_orders_summary"}

MAX_STRING_LENGTH = 200


def validate_tool_call(tool_name: str, arguments: dict) -> dict:
    """
    Server-side validation of all LLM-requested tool calls.
    Raises ValueError with descriptive message if validation fails.
    Returns sanitized arguments dict.
    """
    if tool_name not in VALID_TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    if not arguments:
        return {}

    sanitized = {}
    for key, value in arguments.items():
        if isinstance(value, str):
            value = value.strip()
            if len(value) > MAX_STRING_LENGTH:
                value = value[:MAX_STRING_LENGTH]
            sanitized[key] = value
        else:
            sanitized[key] = value

    if tool_name == "update_customer_profile":
        field = sanitized.get("field", "")
        if field not in VALID_PROFILE_FIELDS:
            raise ValueError(f"Invalid profile field: {field}. Must be one of {VALID_PROFILE_FIELDS}")

    if tool_name == "get_complementary_products":
        pid = sanitized.get("current_product_id", "")
        if not pid.isdigit():
            raise ValueError(f"current_product_id must be a numeric string, got: {pid}")

    return sanitized


def log_tool_call(customer_psid: str, tool_name: str, sanitized_args: dict):
    logger.info(
        "Tool call",
        extra={
            "customer_psid": customer_psid,
            "tool": tool_name,
            "arguments": json.dumps(sanitized_args, ensure_ascii=False),
        },
    )
