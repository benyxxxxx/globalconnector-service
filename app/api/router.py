from fastapi import APIRouter
from app.api import businesses

api_router = APIRouter()
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
