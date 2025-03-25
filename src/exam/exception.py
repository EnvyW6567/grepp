from fastapi import HTTPException, status

from src.core.exception.service_exception import ServiceException


class ExamException(ServiceException):
    pass


class ExamValidationError(ExamException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="EXAM_VALIDATION_ERROR",
        )

    def to_http_exception(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": self.message,
                "error_code": self.error_code,
            }
        )


class ExamCapacityExceededError(ExamException):
    def __init__(self):
        super().__init__(
            message="Exam capacity has been exceeded",
            error_code="EXAM_CAPACITY_EXCEEDED",
        )

    def to_http_exception(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": self.message,
                "error_code": self.error_code,
            }
        )


class ExamNotFound(ExamException):
    def __init__(self, exam_id):
        super().__init__(
            message="Not found exam",
            error_code="EXAM_NOT_FOUND",
            detail={
                exam_id
            }
        )

    def to_http_exception(self):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": self.message,
                "error_code": self.error_code,
            }
        )
