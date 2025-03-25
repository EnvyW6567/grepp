from typing import Optional, Any

from fastapi import HTTPException, status


class ServiceException(Exception):
    def __init__(self, message: str, error_code: Optional[str] = None, detail: Optional[Any] = None):
        self.message = message
        self.error_code = error_code
        self.detail = detail
        super().__init__(self.message)

    def to_http_exception(self):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": self.message,
                "error_code": self.error_code,
                "detail": self.detail
            }
        )
