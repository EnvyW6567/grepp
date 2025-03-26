from typing import Optional

from fastapi import HTTPException, status

from src.core.exception.service_exception import ServiceException


class ReservationException(ServiceException):
    pass


class ReservationValidationFailed(ReservationException):
    def __init__(self):
        super().__init__(
            message="Reservation data validation failed",
            error_code="RESERVATION_VALIDATION_ERROR",
        )

    def to_http_exception(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": self.message,
                "error_code": self.error_code,
            }
        )


class ReservationNotFound(ReservationException):
    def __init__(self, detail: Optional[dict]):
        super().__init__(
            message="Not found reservation",
            error_code="RESERVATION_NOT_FOUND",
            detail=detail
        )

    def to_http_exception(self):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": self.message,
                "error_code": self.error_code,
            }
        )


class NotAllowed(ReservationException):
    def __init__(self):
        super().__init__(
            message="Not allowed request, check your authentication",
            error_code="NOT_ALLOWED",
        )

    def to_http_exception(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": self.message,
                "error_code": self.error_code,
            }
        )
