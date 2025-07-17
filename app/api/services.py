from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import List
from app.database import get_session  # Your DB session dependency
from app.schemas.service import ServiceResponse, ServiceCreate, ServiceUpdate
from app.services.service import ServiceCRUD
from app.auth import get_current_user_id  # Your auth dependency


router = APIRouter(dependencies=[Depends(get_current_user_id)])


@router.get("/", response_model=List[ServiceResponse])
def list_services(
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = ServiceCRUD(session, current_user_id)
    return crud.list_all()


# @router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_service(
    service_in: ServiceCreate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = ServiceCRUD(session, current_user_id)
    service = crud.create(service_in)
    return service


@router.get("/{service_id}", response_model=ServiceResponse)
def read_service(
    service_id: str,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = ServiceCRUD(session, current_user_id)
    service = crud.get(service_id)
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: str,
    service_in: ServiceUpdate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = ServiceCRUD(session, current_user_id)
    service = crud.update(service_id, service_in)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: str,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = ServiceCRUD(session, current_user_id)
    crud.delete(service_id)
    return None


@router.get("/business/{business_id}", response_model=List[ServiceResponse])
def list_services_by_business(
    business_id: str,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
):
    crud = ServiceCRUD(session, current_user_id)
    services = crud.list_by_business(business_id)
    return services
