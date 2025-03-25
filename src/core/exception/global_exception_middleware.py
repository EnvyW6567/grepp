import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            logger.info(f"Incoming request: {request.method} {request.url}")

            response = await call_next(request)
            
            return response

        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")
            logger.error(traceback.format_exc())

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred"
                }
            )
