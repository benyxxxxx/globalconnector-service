from fastapi import APIRouter
from app.api import businesses, services, bookings

api_router = APIRouter()
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
