# app/schemas/booking.py
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.booking import BookingStatus


class BookingBase(BaseModel):
    service_id: str
    user_id: str
    variant_id: Optional[str] = None
    offering_snapshot: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime]
    total_price: Optional[float]
    status: BookingStatus = BookingStatus.PENDING
    attributes: Optional[Dict[str, Any]] = None


class BookingCreate(BaseModel):
    service_id: str
    variant_id: Optional[str] = None
    start_time: datetime
    # end_time: Optional[datetime]
    attributes: Optional[Dict[str, Any]] = None


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    attributes: Optional[Dict[str, Any]] = None


class BookingResponse(BookingBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
