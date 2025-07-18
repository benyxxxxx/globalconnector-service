# app/services/booking_crud.py
from uuid import uuid4
import pprint
from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, and_
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingUpdate
from app.utils.booking_exception import ServiceNotFoundException
from app.models.service import Service


class BookingCRUD:
    def __init__(self, session: Session, current_user_id: str):
        self.session = session
        self.current_user_id = current_user_id

    def get(self, booking_id: str) -> Booking:
        booking = self.session.exec(
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.service))
        ).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking

    def list_user_bookings(self) -> List[Booking]:
        return self.session.exec(
            select(Booking).where(Booking.user_id == self.current_user_id)
        ).all()

    def create(self, booking_in: BookingCreate) -> Booking:
        service = self.session.get(Service, booking_in.service_id)
        if not service:
            raise ServiceNotFoundException(booking_in.service_id)

        # Check for duplicate bookings by same user for overlapping scheduled time
        existing_booking = self.session.exec(
            select(Booking).where(
                and_(
                    Booking.user_id == self.current_user_id,
                    Booking.service_id == booking_in.service_id,
                    Booking.scheduled_at == booking_in.scheduled_at,
                    Booking.status != "cancelled",  # exclude cancelled bookings
                )
            )
        ).first()

        if existing_booking and not booking_in.force_add:
            raise HTTPException(
                status_code=400,
                detail="You already have a booking for this service at the scheduled time.",
            )

        pricing = service.pricing

        # Validate and compute price
        if pricing["type"] == "time_based":
            if booking_in.duration is None:
                raise HTTPException(
                    status_code=400,
                    detail="Duration is required for time-based pricing.",
                )
            if pricing.get("base_price") is None or pricing.get("time_unit") is None:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid time-based pricing configuration on service.",
                )

        snapshot = jsonable_encoder(service)

        booking = Booking(
            id=str(uuid4()),
            service_id=booking_in.service_id,
            user_id=self.current_user_id,
            variant_id=booking_in.variant_id,
            service_snapshot=snapshot,
            duration=booking_in.duration,
            attributes=booking_in.attributes or {},
            scheduled_at=booking_in.scheduled_at,
            # total_price=service.pricing.base_price,  # Simplified, can be computed with variant/tier logic
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)
        return booking

    def update(self, booking_id: str, booking_in: BookingUpdate) -> Booking:
        booking = self.get(booking_id)
        if booking.user_id != self.current_user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this booking"
            )

        for key, value in booking_in.model_dump(exclude_unset=True).items():
            setattr(booking, key, value)

        booking.updated_at = datetime.now(timezone.utc)
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)
        return booking

    def delete(self, booking_id: str) -> None:
        booking = self.get(booking_id)
        if booking.user_id != self.current_user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this booking"
            )
        self.session.delete(booking)
        self.session.commit()
