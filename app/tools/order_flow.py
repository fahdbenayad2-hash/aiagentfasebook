from app.database import SessionLocal
from app.models import Customer, Order, OrderItem, Product
from app.models.session import OrderDraft
from app.services.logging_service import logger
from app.services.notification_service import send_telegram_notification


async def create_order(sender_id: str, draft: OrderDraft) -> Order:
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(
            Customer.platform_user_id == sender_id,
            Customer.platform == "facebook"
        ).first()
        if not customer:
            customer = Customer(
                platform_user_id=sender_id,
                platform="facebook",
                name=draft.customer_name,
                phone=draft.phone,
                state=draft.wilaya,
                address=draft.address
            )
            db.add(customer)
            db.flush()

        product = db.query(Product).filter(Product.id == draft.product_id).first()
        total = product.price * draft.quantity if product else 0

        order = Order(
            customer_id=customer.id,
            status="pending",
            total_price=total,
            notes=f"المقاس: {draft.size}, اللون: {draft.color}"
        )
        db.add(order)
        db.flush()

        if product:
            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=draft.quantity,
                price_at_time=product.price
            )
            db.add(item)
            product.stock -= draft.quantity

        db.commit()

        msg = (
            f"🛍️ طلبية جديدة #{order.id}\n"
            f"👤 {draft.customer_name}\n"
            f"📱 {draft.phone}\n"
            f"🛒 {draft.product_name} | {draft.size} | {draft.color} × {draft.quantity}\n"
            f"💰 {total} دج\n"
            f"📍 ولاية {draft.wilaya} — {draft.address}\n"
        )
        try:
            await send_telegram_notification(msg)
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")

        return order
    finally:
        db.close()
