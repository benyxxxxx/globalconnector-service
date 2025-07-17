from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from pydantic import BaseModel, ConfigDict


# Enums
class PricingType(str, Enum):
    FLAT = "flat"
    TIME_BASED = "time_based"


class TimeUnit(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class VariantType(str, Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"


# Pydantic Models for JSON fields
class PricingTier(BaseModel):
    duration: int
    price: float


class Pricing(BaseModel):
    type: PricingType
    base_price: float
    time_unit: Optional[TimeUnit] = None
    tiers: Optional[List[PricingTier]] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None


class VariantOption(BaseModel):
    name: str
    price_change: float
    available: bool = True


class Variant(BaseModel):
    name: str
    type: VariantType
    required: bool
    options: List[VariantOption]


# SQLModel Tables
class Service(SQLModel, table=True):
    __tablename__ = "services"

    id: str = Field(primary_key=True)

    name: str = Field(index=True)
    description: Optional[str] = None
    business_id: str = Field(foreign_key="businesses.id", index=True)
    
    # JSON field for pricing
    pricing: Pricing = Field(sa_column=Column(JSON))
    
    # JSON field for variants
    variants: Optional[List[Variant]] = Field(default=None, sa_column=Column(JSON))
    
    # JSON field for flexible metadata
    attributes: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default=None)