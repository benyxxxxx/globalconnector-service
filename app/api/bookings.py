# app/api/bookings.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import List
from app.database import get_session
from app.services.booking import BookingCRUD
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.auth import get_current_user_id

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = BookingCRUD(session, current_user_id)
    return crud.create(booking_in)


@router.get("/", response_model=List[BookingResponse])
def list_my_bookings(
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = BookingCRUD(session, current_user_id)
    return crud.list_user_bookings()


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: str,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = BookingCRUD(session, current_user_id)
    booking = crud.get(booking_id)
    if booking.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: str,
    booking_in: BookingUpdate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = BookingCRUD(session, current_user_id)
    return crud.update(booking_id, booking_in)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: str,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = BookingCRUD(session, current_user_id)
    crud.delete(booking_id)
    return None
