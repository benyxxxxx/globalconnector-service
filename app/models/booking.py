from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, JSON, Relationship


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: str = Field(primary_key=True, index=True)
    service_id: str = Field(index=True, foreign_key="services.id")
    user_id: str = Field(index=True)

    variant_id: Optional[str] = Field(default=None, index=True)

    # JSON fields
    offering_snapshot: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON))

    start_time: datetime
    end_time: Optional[datetime] = Field(default=None)

    total_price: Optional[float] = Field(default=None)
    status: BookingStatus = Field(default=BookingStatus.PENDING)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # 👇 Relationship to Service
    service: Optional["Service"] = Relationship(back_populates="bookings")
