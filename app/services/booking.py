# app/services/booking_crud.py
from uuid import uuid4
import pprint
from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlmodel import Session, select
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
        booking = self.session.exec(select(Booking).where(Booking.id == booking_id)).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking

    def list_user_bookings(self) -> List[Booking]:
        return self.session.exec(select(Booking).where(Booking.user_id == self.current_user_id)).all()

    def create(self, booking_in: BookingCreate) -> Booking:
            service = self.session.get(Service, booking_in.service_id)
            if not service:
                raise ServiceNotFoundException(booking_in.service_id)

            snapshot = jsonable_encoder(service)

            pprint.pprint(snapshot)

            booking = Booking(
                id=str(uuid4()),
                service_id=booking_in.service_id,
                user_id=self.current_user_id,
                variant_id=booking_in.variant_id,
                # offering_snapshot=snapshot,
                offering_snapshot={},
                attributes=booking_in.attributes or {},
                start_time=booking_in.start_time,
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
            raise HTTPException(status_code=403, detail="Not authorized to update this booking")

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
            raise HTTPException(status_code=403, detail="Not authorized to delete this booking")
        self.session.delete(booking)
        self.session.commit()
