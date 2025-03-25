from fastapi import FastAPI

from src.core.exception.global_exception_middleware import GlobalExceptionMiddleware
from src.db.db import Base, engine
from src.exam.router import admin_router as admin_exam_router
from src.exam.router import router as exam_router
from src.member.router import router as member_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="grepp")
app.add_middleware(GlobalExceptionMiddleware)

app.include_router(member_router)
app.include_router(exam_router)
app.include_router(admin_exam_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
