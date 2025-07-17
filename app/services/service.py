from typing import List, Optional
from sqlmodel import select, Session
from fastapi import HTTPException
from datetime import datetime, timezone
from uuid import uuid4
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate

class ServiceCRUD:
    def __init__(self, session: Session, current_user_id: str):
        self.session = session
        self.current_user_id = current_user_id

    def get(self, service_id: str) -> Optional[Service]:
        statement = select(Service).where(Service.id == service_id)
        service = self.session.exec(statement).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        # Optionally check ownership here if needed
        return service


    def list_all(self) -> List[Service]:
        statement = select(Service)
        return self.session.exec(statement).all()

    def list_by_business(self, business_id: str) -> List[Service]:
        statement = select(Service).where(Service.business_id == business_id)
        return self.session.exec(statement).all()

    def create(self, service_in: ServiceCreate) -> Service:
        service = Service(
            id=str(uuid4()),
            name=service_in.name,
            description=service_in.description,
            owner_id=self.current_user_id,
            business_id=service_in.business_id,
            pricing=service_in.pricing.model_dump(),
            variants=service_in.variants,
            attributes=service_in.attributes,  
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(service)
        self.session.commit()
        self.session.refresh(service)
        return service

    def update(self, service_id: str, service_in: ServiceUpdate) -> Service:
        service = self.get(service_id)
        if service.owner_id != self.current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this service")

        for field, value in service_in.model_dump(exclude_unset=True).items():
            if field == "attributes":
                setattr(service, "attributes", value)
            else:
                setattr(service, field, value)
        service.updated_at = datetime.now(timezone.utc)
        self.session.add(service)
        self.session.commit()
        self.session.refresh(service)
        return service

    def delete(self, service_id: str) -> None:
        service = self.get(service_id)
        if service.owner_id != self.current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this service")
        self.session.delete(service)
        self.session.commit()
