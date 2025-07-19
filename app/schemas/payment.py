from pydantic import BaseModel as PydanticBaseModel
from typing import Optional, Dict, Any
from enum import Enum
from decimal import Decimal
from datetime import datetime
from app.models.payment import PaymentStatus, PaymentMethod


# -----------------------------
# Shared base schema
# -----------------------------
class PaymentBase(PydanticBaseModel):
    booking_id: str
    status: PaymentStatus = PaymentStatus.PENDING
    amount: Decimal
    currency: str = "USD"
    method: PaymentMethod = PaymentMethod.CARD
    external_id: Optional[str] = None
    transaction_id: Optional[str] = None
    provider: str = ""
    paid_at: Optional[datetime] = None
    payment_metadata: Dict[str, Any] = {}

    # class Config:
    #     orm_mode = True


# -----------------------------
# Create schema
# -----------------------------
class PaymentCreate(PydanticBaseModel):
    method: PaymentMethod = PaymentMethod.CARD


# -----------------------------
# Update schema
# -----------------------------
class PaymentUpdate(PydanticBaseModel):
    status: Optional[PaymentStatus] = None
    method: Optional[PaymentMethod] = None
    external_id: Optional[str] = None
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    payment_metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


# -----------------------------
# Read schema (e.g. for GET response)
# -----------------------------
class PaymentRead(PaymentBase):
    id: str
    created_at: datetime
    updated_at: datetime
