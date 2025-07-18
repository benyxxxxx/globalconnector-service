from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import List
from app.database import get_session  # Your DB session dependency
from app.schemas.service import ServiceResponse, ServiceCreate, ServiceUpdate
from app.services.service import ServiceCRUD
from app.auth import get_current_user_id  # Your auth dependency
from .deps import get_service_crud


router = APIRouter(dependencies=[Depends(get_current_user_id)])


@router.get("/", response_model=List[ServiceResponse])
def list_services(
    service_crud: ServiceCRUD = Depends(get_service_crud),
):
    return service_crud.list_all()


@router.get("/my", response_model=List[ServiceResponse])
async def get_owner_businesses(service_crud: ServiceCRUD = Depends(get_service_crud)):
    return service_crud.get_by_owner_id()


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_in: ServiceCreate, service_crud: ServiceCRUD = Depends(get_service_crud)
):
    service = service_crud.create(service_in)
    return service


@router.get("/{service_id}", response_model=ServiceResponse)
def read_service(
    service_id: str, service_crud: ServiceCRUD = Depends(get_service_crud)
):
    service = service_crud.get(service_id)
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: str,
    service_in: ServiceUpdate,
    service_crud: ServiceCRUD = Depends(get_service_crud),
):
    service = service_crud.update(service_id, service_in)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: str, service_crud: ServiceCRUD = Depends(get_service_crud)
):
    service_crud.delete(service_id)
    return None


@router.get("/business/{business_id}", response_model=List[ServiceResponse])
def list_services_by_business(
    business_id: str, service_crud: ServiceCRUD = Depends(get_service_crud)
):
    services = service_crud.list_by_business(business_id)
    return services
