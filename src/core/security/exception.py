from fastapi import HTTPException, status

from src.core.exception.security_exception import SecurityException


class TokenValidationFailed(SecurityException):
    def __init__(self):
        super().__init__(
            message="Token validation falied, not authenticated",
            error_code="TOKEN_VALIDATION_FAILED",
        )

    def to_http_exception(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": self.message,
                "error_code": self.error_code,
            }
        )
