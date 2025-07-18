from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.schemas.business import (
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
    BusinessFilter,
)
from app.models.business import BusinessType
from app.services.business import BusinessCRUD
from app.api.deps import get_business_crud
from app.auth import get_current_user_id

router = APIRouter(dependencies=[Depends(get_current_user_id)])


@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    business_create: BusinessCreate,
    business_crud: BusinessCRUD = Depends(get_business_crud),
):
    """Create a new business"""
    return business_crud.create(business_create)


@router.get("/", response_model=List[BusinessResponse])
async def get_businesses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    owner_id: Optional[str] = Query(None),
    business_type: Optional[BusinessType] = Query(None, alias="type"),
    name: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    business_crud: BusinessCRUD = Depends(get_business_crud),
):
    """Get all businesses with optional filtering"""
    filters = BusinessFilter(
        owner_id=owner_id, type=business_type, name=name, location=location
    )
    return business_crud.get_all(skip=skip, limit=limit, filters=filters)


@router.get("/my", response_model=List[BusinessResponse])
async def get_owner_businesses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    business_crud: BusinessCRUD = Depends(get_business_crud),
):
    """Get businesses by owner ID"""
    return business_crud.get_by_owner_id(
        business_crud.current_user_id, skip=skip, limit=limit
    )


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: str, business_crud: BusinessCRUD = Depends(get_business_crud)
):
    """Get business by ID"""
    business = business_crud.get_by_id(business_id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id {business_id} not found",
        )
    return business


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: str,
    business_update: BusinessUpdate,
    business_crud: BusinessCRUD = Depends(get_business_crud),
):
    """Update business by ID"""
    return business_crud.update(business_id, business_update)


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: str,
    business_crud: BusinessCRUD = Depends(get_business_crud),
):
    """Delete business by ID"""
    business_crud.delete(business_id)
