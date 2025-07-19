from datetime import datetime, timezone
from typing import List
from sqlmodel import Session, select
from app.utils.ids import generate_unique_id
from app.schemas.payment import PaymentBase, PaymentUpdate, PaymentCreate
from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, payment_id: str) -> Payment:
        statement = select(Payment).where(Payment.id == payment_id)

        payment = self.session.exec(statement).first()
        return payment

    def list_by_booking(self, booking_id: str) -> List[Payment]:
        statement = (
            select(Payment)
            .where(Payment.booking_id == booking_id)
            .order_by(Payment.created_at.desc())
        )
        return self.session.exec(statement).all()

    def create(self, payment_in: PaymentCreate, booking_id: str) -> Payment:

        payment_id = generate_unique_id()

        payment = Payment(
            id=payment_id,
            booking_id=booking_id,
            **payment_in.model_dump(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def update(self, payment_id: str, payment_in: PaymentUpdate) -> Payment:
        payment = self.get(payment_id)

        for key, value in payment_in.model_dump(exclude_unset=True).items():
            setattr(payment, key, value)

        payment.updated_at = datetime.now(timezone.utc)
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment
