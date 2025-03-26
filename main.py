import os

from dotenv import load_dotenv
from fastapi import FastAPI

from src.core.exception.global_exception_middleware import GlobalExceptionMiddleware
from src.core.logger.logger import setup_logging
from src.db.db import Base, engine
from src.exam.admin_router import admin_router as admin_exam_router
from src.exam.router import router as exam_router
from src.member.router import router as member_router
from src.reservation.admin_router import admin_router as admin_reservation_router
from src.reservation.router import router as reservation_router

load_dotenv()

Base.metadata.create_all(bind=engine)

setup_logging()

app = FastAPI(title="grepp")
app.add_middleware(GlobalExceptionMiddleware)

app.include_router(member_router)
app.include_router(exam_router)
app.include_router(admin_exam_router)
app.include_router(reservation_router)
app.include_router(admin_reservation_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv('SERVER_PORT', 8000)), reload=True)
