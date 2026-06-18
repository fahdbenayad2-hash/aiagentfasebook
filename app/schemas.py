from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock: int = 0
    active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock: Optional[int] = None
    active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Customer Schemas
class CustomerBase(BaseModel):
    platform_user_id: str
    platform: str
    name: Optional[str] = None
    phone: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Order Schemas
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_time: int
    product: ProductResponse

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]
    notes: Optional[str] = None

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: str
    total_price: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    customer: CustomerResponse
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationResponse(BaseModel):
    id: int
    platform_user_id: str
    platform: str
    current_state: str
    context_data: Dict[str, Any]
    last_message_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# AI Response Schema
class AIResponse(BaseModel):
    intent: str = Field(..., description="order|faq|browse|handoff|greeting|collect_info")
    response: str = Field(..., description="Response text for customer")
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    product_mentions: List[str] = Field(default_factory=list)
    needs_human: bool = False
    state_transition: Optional[str] = None
