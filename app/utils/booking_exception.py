from fastapi import HTTPException, status


class ServiceNotFoundException(HTTPException):
    def __init__(self, id: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid service id {id}",
        )
