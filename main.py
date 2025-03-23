from fastapi import FastAPI

from src.db.db import Base, engine
from src.member.router import router as member_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="grepp")

app.include_router(member_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
