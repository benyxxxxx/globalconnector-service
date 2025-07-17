from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from app.api.router import api_router
# from app.core.exceptions import setup_exception_handlers
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Exception handlers
# setup_exception_handlers(app)

# # Include routers
# app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}