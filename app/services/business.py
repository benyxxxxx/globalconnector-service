from sqlmodel import Session, select, and_, or_
from datetime import timezone
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.business import Business, BusinessType
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessFilter
from app.utils.business_exceptions import (
    BusinessNotFoundException,
    BusinessAlreadyExistsException,
    BusinessNameConflictException,
    UnauthorizedBusinessAccessException
)

class BusinessCRUD:
    def __init__(self, session: Session):
        self.session = session
    
    def generate_business_id(self) -> str:
        """Generate a unique business ID"""
        return str(uuid.uuid4())
    
    def check_name_conflict(self, name: str, owner_id: str, exclude_id: Optional[str] = None) -> bool:
        """Check if business name already exists for the owner"""
        statement = select(Business).where(
            and_(
                Business.name == name,
                Business.owner_id == owner_id
            )
        )
        
        if exclude_id:
            statement = statement.where(Business.id != exclude_id)
        
        existing_business = self.session.exec(statement).first()
        return existing_business is not None
    
    def create(self, business_create: BusinessCreate, owner_id: str) -> Business:
        """Create a new business"""
        business_id = self.generate_business_id()
        
        # Check if business already exists (shouldn't happen with UUID)
        existing_business = self.get_by_id(business_id)
        if existing_business:
            raise BusinessAlreadyExistsException(business_id)
        
        # Check for name conflict within owner's businesses
        if self.check_name_conflict(business_create.name, owner_id):
            raise BusinessNameConflictException(business_create.name, owner_id)
        
        # Create business
        business_data = business_create.model_dump()
        business_data['owner_id'] = owner_id
        business = Business(id=business_id, **business_data)
        
        self.session.add(business)
        self.session.commit()
        self.session.refresh(business)
        return business
    
    def get_by_id(self, business_id: str) -> Optional[Business]:
        """Get business by ID"""
        statement = select(Business).where(Business.id == business_id)
        return self.session.exec(statement).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, filters: Optional[BusinessFilter] = None) -> List[Business]:
        """Get all businesses with optional filtering"""
        statement = select(Business)
        
        if filters:
            conditions = []
            
            if filters.owner_id:
                conditions.append(Business.owner_id == filters.owner_id)
            
            if filters.type:
                conditions.append(Business.type == filters.type)
            
            if filters.name:
                # Case-insensitive name search
                conditions.append(Business.name.ilike(f"%{filters.name}%"))
            
            if filters.location:
                # Case-insensitive address search
                conditions.append(Business.address.ilike(f"%{filters.location}%"))
            
            if conditions:
                statement = statement.where(and_(*conditions))
        
        statement = statement.offset(skip).limit(limit).order_by(Business.created_at.desc())
        return self.session.exec(statement).all()
    
    def get_by_owner_id(self, owner_id: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """Get businesses by owner ID"""
        statement = select(Business).where(Business.owner_id == owner_id)\
                   .offset(skip).limit(limit).order_by(Business.created_at.desc())
        return self.session.exec(statement).all()
    
    def get_by_type(self, business_type: BusinessType, skip: int = 0, limit: int = 100) -> List[Business]:
        """Get businesses by type"""
        statement = select(Business).where(Business.type == business_type)\
                   .offset(skip).limit(limit).order_by(Business.created_at.desc())
        return self.session.exec(statement).all()
    
    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """Search businesses by name (case-insensitive)"""
        statement = select(Business).where(Business.name.ilike(f"%{name}%"))\
                   .offset(skip).limit(limit).order_by(Business.created_at.desc())
        return self.session.exec(statement).all()
    
    def search_by_location(self, location: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """Search businesses by location/address (case-insensitive)"""
        statement = select(Business).where(Business.address.ilike(f"%{location}%"))\
                   .offset(skip).limit(limit).order_by(Business.created_at.desc())
        return self.session.exec(statement).all()
    
    def update(self, business_id: str, business_update: BusinessUpdate, user_id: str) -> Business:
        """Update business"""
        business = self.get_by_id(business_id)
        if not business:
            raise BusinessNotFoundException(business_id)
        
        update_data = business_update.model_dump(exclude_unset=True)
        
        # Check for name conflict if name is being updated
        if 'name' in update_data:
            new_name = update_data['name']
            owner_id = update_data.get('owner_id', business.owner_id)
            
            if self.check_name_conflict(new_name, owner_id, exclude_id=business_id):
                raise BusinessNameConflictException(new_name, owner_id)

        if user_id != business.owner_id:
            raise UnauthorizedBusinessAccessException(business_id)
            
        # Apply updates
        for field, value in update_data.items():
            setattr(business, field, value)
        
        business.updated_at = datetime.now(timezone.utc)
        self.session.add(business)
        self.session.commit()
        self.session.refresh(business)
        return business
    
    def delete(self, business_id: str, user_id: str) -> bool:
        """Delete business"""
        business = self.get_by_id(business_id)

        if not business:
            raise BusinessNotFoundException(business_id)

        if user_id != business.owner_id:
            raise UnauthorizedBusinessAccessException(business_id)
        
        self.session.delete(business)
        self.session.commit()
        return True
    
    def verify_ownership(self, business_id: str, owner_id: str) -> bool:
        """Verify if user owns the business"""
        business = self.get_by_id(business_id)
        if not business:
            raise BusinessNotFoundException(business_id)
        
        return business.owner_id == owner_id
    
    def transfer_ownership(self, business_id: str, new_owner_id: str) -> Business:
        """Transfer business ownership"""
        business = self.get_by_id(business_id)
        if not business:
            raise BusinessNotFoundException(business_id)
        
        # Check if new owner already has a business with same name
        if self.check_name_conflict(business.name, new_owner_id):
            raise BusinessNameConflictException(business.name, new_owner_id)
        
        business.owner_id = new_owner_id
        business.updated_at = datetime.utcnow()
        
        self.session.add(business)
        self.session.commit()
        self.session.refresh(business)
        return business
    
    def get_business_count_by_type(self) -> dict:
        """Get count of businesses by type"""
        from sqlmodel import func
        
        statement = select(Business.type, func.count(Business.id))\
                   .group_by(Business.type)
        
        results = self.session.exec(statement).all()
        return {business_type: count for business_type, count in results}
    
    def get_businesses_by_owner_count(self, owner_id: str) -> int:
        """Get count of businesses owned by a specific owner"""
        from sqlmodel import func
        
        statement = select(func.count(Business.id)).where(Business.owner_id == owner_id)
    #     return self.session.exec(statement).one()