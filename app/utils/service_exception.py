from fastapi import HTTPException, status


class ServiceAlreadyExistsException(HTTPException):
    def __init__(self, name: str, business_id: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service {name} for {business_id} already exists",
        )
