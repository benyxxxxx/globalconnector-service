from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import List
from app.database import get_session
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentResponse, PaymentRequest

from app.security import get_current_user_id
from .deps import get_payment_service

router = APIRouter()


@router.get("/{booking_id}/payments", response_model=List[PaymentResponse])
def get_payments(
    booking_id: str,
    payment_service: PaymentService = Depends(get_payment_service),
):
    return payment_service.list_by_booking(booking_id=booking_id)


@router.post(
    "/{booking_id}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    booking_id: str,
    payment_in: PaymentRequest,
    payment_service: PaymentService = Depends(get_payment_service),
):
    return payment_service.create_payment(booking_id, payment_in=payment_in)
