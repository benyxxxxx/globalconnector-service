from urllib.parse import urlencode, quote
from typing import List
from decimal import Decimal
from app.repositories.payment_repository import PaymentRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.service_repository import ServiceRepository
from app.exceptions.booking_exception import BookingNotFoundException
from app.utils.ids import generate_random_base58_key
from app.schemas.payment import (
    PaymentCreate,
    PaymentBase,
    PaymentRequest,
    PaymentStatus,
    PaymentMethod,
)
from app.config import settings
from sqlmodel import Session
from app.exceptions.payment_exceptions import (
    PaymentNotFoundException,
    UnauthorizedPaymentAccessException,
)
from app.models.payment import Payment, PaymentProvider


class PaymentService:
    def __init__(self, session: Session):
        self.repo = PaymentRepository(session)
        self.booking_repo = BookingRepository(session)
        self.service_repo = ServiceRepository(session)

    def get(self, payment_id: str) -> Payment:
        payment_data = self.repo.get(payment_id=payment_id)

        if not payment_data:
            raise PaymentNotFoundException(payment_id)

        return payment_data

    def list_by_booking(self, booking_id: str) -> List[Payment]:
        return self.repo.list_by_booking(booking_id)

    def get_payment_provider(self, method: PaymentMethod):
        if method == PaymentMethod.MANDEL_COIN:
            return PaymentProvider.SOLANA
        return ""

    def get_solana_address(self):
        return {
            "destination": settings.SOLANA_DESTINATION_ADDRESS,
            "mint": settings.MANDEL_COIN_MINT_ADDRESS,
        }

    def generate_solana_pay_url(
        self,
        amount: float,
        reference: str,
        label: str = None,
        message: str = None,
        memo: str = None,
    ) -> str:
        base = f"solana:{settings.SOLANA_DESTINATION_ADDRESS}"

        params = {}

        if amount is not None:
            params["amount"] = str(amount)
        if reference:
            params["reference"] = reference
        if label:
            params["label"] = label
        if message:
            params["message"] = message
        if memo:
            params["memo"] = memo

        params["spl-token"] = settings.MANDEL_COIN_MINT_ADDRESS

        query = urlencode(params, quote_via=quote)

        return f"{base}?{query}" if query else base

    def get_payment_meta_for(self, method: PaymentMethod):
        if method == PaymentMethod.MANDEL_COIN:
            return self.get_solana_address()
        return {}

    def create_payment(self, booking_id: str, payment_in: PaymentRequest) -> Payment:
        booking = self.booking_repo.get(booking_id)
        if not booking:
            raise BookingNotFoundException(booking_id)

        amount = booking.total_price or 0

        payments = self.repo.list_by_booking(booking_id)
        if payments and not payment_in.force_add:
            return payments[0]

        reference = generate_random_base58_key()
        payment_meta = self.get_payment_meta_for(payment_in.payment_method)
        payment_meta["solana_pay_link"] = self.generate_solana_pay_url(10, reference)

        payment_data = PaymentCreate(
            amount=amount,
            status=PaymentStatus.PENDING,
            currency=booking.service.currency,
            transaction_id="",
            external_id=reference,
            payment_method=payment_in.payment_method,
            payment_metadata=payment_meta,
            provider=self.get_payment_provider(payment_in.payment_method),
        )

        payment_created = self.repo.create(
            payment_in=payment_data, booking_id=booking_id
        )
        return payment_created
