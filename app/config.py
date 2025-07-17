from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "GlobalConnector"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "GlobalConnector"
    
    # Database
    DATABASE_URL: str 
    
    # Security
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]

    @field_validator("DATABASE_URL", "SECRET_KEY")
    @classmethod
    def must_not_be_empty(cls, v, field):
        if not v:
            raise ValueError(f"{field.name.upper()} must not be empty")

    
    class Config:
        env_file = ".env"

settings = Settings()