from pydantic import BaseModel as PydanticBaseModel
from typing import Optional, Dict, Any
from enum import Enum
from decimal import Decimal
from datetime import datetime
from app.models.payment import PaymentStatus, PaymentMethod, PaymentProvider


# -----------------------------
# Shared base schema
# -----------------------------
class PaymentBase(PydanticBaseModel):
    id: str
    booking_id: str
    status: PaymentStatus = PaymentStatus.PENDING
    amount: Decimal
    currency: str = "USD"
    payment_method: PaymentMethod = PaymentMethod.CARD
    external_id: Optional[str] = None
    transaction_id: Optional[str] = None
    provider: PaymentProvider = ""
    paid_at: Optional[datetime] = None
    payment_metadata: Dict[str, Any] = {}

    # class Config:
    #     orm_mode = True


# -----------------------------
# Create schema
# -----------------------------
class PaymentRequest(PydanticBaseModel):
    payment_method: PaymentMethod
    force_add: Optional[bool] = False


class PaymentCreate(PydanticBaseModel):
    status: PaymentStatus = PaymentStatus.PENDING
    amount: Decimal
    currency: str = "USD"
    payment_method: PaymentMethod = PaymentMethod.CARD
    external_id: Optional[str] = None
    transaction_id: Optional[str] = None
    provider: PaymentProvider = ""
    payment_metadata: Dict[str, Any] = {}


# -----------------------------
# Update schema
# -----------------------------
class PaymentUpdate(PydanticBaseModel):
    status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    external_id: Optional[str] = None
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    payment_metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


# -----------------------------
# Read schema (e.g. for GET response)
# -----------------------------
class PaymentResponse(PaymentBase):
    id: str
    created_at: datetime
    updated_at: datetime
