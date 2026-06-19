from enum import Enum


class CustomerIntent(Enum):
    # Tier 1 — High Volume (autonomous)
    ORDER_STATUS = "order_status"
    ORDER_CANCEL = "order_cancel"
    PRODUCT_INFO = "product_info"
    PRICE_INQUIRY = "price_inquiry"
    DELIVERY_DELAY = "delivery_delay"
    RETURN_EXCHANGE = "return_exchange"
    STORE_HOURS = "store_hours"
    PAYMENT_METHODS = "payment_methods"

    # Tier 2 — Moderate (tool-assisted)
    COMPLAINT_PRODUCT = "complaint_product"
    COMPLAINT_SERVICE = "complaint_service"
    PROMO_INQUIRY = "promo_inquiry"
    BULK_ORDER = "bulk_order"

    # Tier 3 — Escalate
    LEGAL_THREAT = "legal_threat"
    PAYMENT_DISPUTE = "payment_dispute"
    FRAUD_SUSPICION = "fraud_suspicion"
    OUT_OF_SCOPE = "out_of_scope"

    # Fallback
    UNKNOWN = "unknown"
