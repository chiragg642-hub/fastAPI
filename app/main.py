from fastapi import FastAPI # type: ignore
from sqlmodel import SQLModel
from . database import engine
from .routers import post, user, auth

SQLModel.metadata.create_all(engine)

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Welcome to my api!"}