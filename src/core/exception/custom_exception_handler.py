import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from main import app
from src.core.exception.service_exception import ServiceException

logger = logging.getLogger(__name__)


@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
    logger.warning(f"HTTP Exception: {exc.error_code} - {exc.detail}")

    http_exception = exc.to_http_exception()

    return JSONResponse(
        status_code=http_exception.status_code,
        content={
            "message": http_exception.message,
            "detail": http_exception.detail
        }
    )
