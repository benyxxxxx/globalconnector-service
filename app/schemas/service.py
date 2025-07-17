
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.service import Pricing, Variant

# Request/Response Models
class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    business_id: str
    pricing: Pricing
    variants: Optional[List[Variant]] = None
    metadata: Optional[Dict[str, Any]] = None


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pricing: Optional[Pricing] = None
    variants: Optional[List[Variant]] = None
    metadata: Optional[Dict[str, Any]] = None


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    business_id: str
    pricing: Pricing
    variants: Optional[List[Variant]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
