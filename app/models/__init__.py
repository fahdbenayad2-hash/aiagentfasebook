from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    platform_user_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False)
    name = Column(String)
    phone = Column(String)
    state = Column(String)
    address = Column(Text)
    preferred_size = Column(String, nullable=True)
    fabric_preference = Column(String, nullable=True)
    last_orders_summary = Column(String, nullable=True)
    interaction_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = relationship("Order", back_populates="customer")
    conversations = relationship("Conversation", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    category = Column(String)
    image_url = Column(String)
    stock = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    complementary_product_ids = Column(String, nullable=True)
    colors = Column(String, nullable=True)
    sizes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_colors(self) -> list[str]:
        if not self.colors:
            return []
        return [c.strip() for c in self.colors.split(",")]

    def set_colors(self, color_list: list[str]):
        from app.utils.arabic import normalize_arabic
        normalized = [normalize_arabic(c) for c in color_list]
        self.colors = ",".join(normalized)

    def get_sizes(self) -> list[str]:
        if not self.sizes:
            return []
        return [s.strip() for s in self.sizes.split(",")]

    def set_sizes(self, size_list: list[str]):
        self.sizes = ",".join([s.strip().upper() for s in size_list])

    def has_color(self, color: str) -> bool:
        from app.utils.arabic import normalize_arabic
        target = normalize_arabic(color)
        return target in [normalize_arabic(c) for c in self.get_colors()]

    def has_size(self, size: str) -> bool:
        return size.strip().upper() in self.get_sizes()

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String, default="pending")
    total_price = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    price_at_time = Column(Integer)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class SessionRecord(Base):
    __tablename__ = "session_records"

    sender_id = Column(String, primary_key=True)
    page_id = Column(String, primary_key=True)
    state_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    platform_user_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    current_state = Column(String, default="IDLE")
    context_data = Column(JSON, default=dict)
    messages = Column(JSON, default=list)
    manual_mode = Column(Boolean, default=False)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="conversations")


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    message_count = Column(Integer, default=0)
    completed_order = Column(Boolean, default=False)
    escalated = Column(Boolean, default=False)
    product_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    credits = Column(Integer, default=0)
    is_developer = Column(Boolean, default=False)
    notification_phone = Column(String, nullable=True)
    notify_new_order = Column(Boolean, default=True)
    notify_handoff = Column(Boolean, default=True)
    telegram_chat_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FacebookConnection(Base):
    __tablename__ = "facebook_connections"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(String, unique=True, nullable=False)
    page_name = Column(String, nullable=False)
    page_access_token_encrypted = Column(Text, nullable=False)
    user_access_token_encrypted = Column(Text, nullable=True)
    user_token_expires_at = Column(DateTime, nullable=True)
    connected_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    store_name = Column(String, nullable=True)

