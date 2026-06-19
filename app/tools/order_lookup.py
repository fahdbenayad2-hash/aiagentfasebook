from app.database import SessionLocal
from app.models import Order, Customer, OrderItem
from app.services.logging_service import logger


class OrderNotFoundError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


async def lookup_order(order_id: str, sender_id: str) -> dict:
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == int(order_id)).first()
        if not order:
            raise OrderNotFoundError(f"Order #{order_id} not found")

        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        if not customer:
            raise PermissionDeniedError("Order has no customer")

        if customer.platform_user_id != sender_id:
            raise PermissionDeniedError(
                f"sender {sender_id} does not own order #{order_id}"
            )

        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        items_data = []
        for item in items:
            items_data.append({
                "product_name": item.product.name if item.product else "Unknown",
                "quantity": item.quantity,
                "price": item.price_at_time
            })

        phone_last4 = (customer.phone or "0000")[-4:]

        return {
            "order_id": order.id,
            "status": order.status,
            "wilaya": customer.state or "",
            "expected_delivery": "",
            "total_price": order.total_price,
            "items": items_data,
            "phone_last4": phone_last4
        }

    except OrderNotFoundError:
        return {"error": "not_found", "order_id": order_id}
    except PermissionDeniedError:
        logger.warning(f"Permission denied: {sender_id} tried to access order #{order_id}")
        return {"error": "permission_denied"}
    except ValueError:
        return {"error": "invalid_id"}
    finally:
        db.close()
