from fastapi import Depends
from sqlmodel import Session

from app.services.business import BusinessCRUD  # or repositories.business if you renamed it
from app.database import get_session  # adjust the import path based on your project

from app.services.business import BusinessCRUD

def get_business_crud(session: Session = Depends(get_session)) -> BusinessCRUD:
    return BusinessCRUD(session)