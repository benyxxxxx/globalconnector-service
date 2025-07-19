from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import selectinload
from decimal import Decimal
from sqlmodel import Session, select, and_
from app.utils.ids import generate_unique_id
from fastapi.encoders import jsonable_encoder
from app.schemas.payment import (
    PaymentCreate,
    PaymentStatus,
    PaymentMethod,
    PaymentBase,
    PaymentUpdate,
)
from app.schemas.booking import BookingCreate, BookingUpdate
from app.models.service import Service
from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, payment_id: str) -> Payment:
        statement = select(Payment).where(Payment.id == payment_id)

        payment = self.session.exec(statement).first()
        return payment

    def list_by_booking(self, booking_id: str) -> List[Payment]:
        statement = select(Payment).where(Payment.booking_id == booking_id)
        return self.session.exec(statement).all()

    def create(self, payment_in: PaymentBase, booking_id: str) -> Payment:

        payment_id = generate_unique_id()

        payment = Payment(
            id=payment_id,
            booking_id=booking_id,
            **payment_in,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def update(self, booking_id: str, payment_in: PaymentUpdate) -> Payment:
        payment = self.get(booking_id)

        for key, value in payment_in.model_dump(exclude_unset=True).items():
            setattr(payment, key, value)

        payment.updated_at = datetime.now(timezone.utc)
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment
