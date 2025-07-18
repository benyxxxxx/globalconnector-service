from fastapi import Depends
from sqlmodel import Session

from app.services.business import (
    BusinessCRUD,
)  # or repositories.business if you renamed it
from app.services.service import ServiceCRUD
from app.database import get_session  # adjust the import path based on your project

from app.services.business import BusinessCRUD
from app.auth import get_current_user_id


def get_business_crud(session: Session = Depends(get_session), current_user_id: str = Depends(get_current_user_id)) -> BusinessCRUD:
    return BusinessCRUD(session, current_user_id)



def get_service_crud(session: Session = Depends(get_session), current_user_id: str = Depends(get_current_user_id)) -> ServiceCRUD:
    return ServiceCRUD(session, current_user_id)