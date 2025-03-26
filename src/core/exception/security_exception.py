from typing import Optional

from fastapi import HTTPException, status


class SecurityException(Exception):
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def to_http_exception(self):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": self.message,
                "error_code": self.error_code,
            }
        )
