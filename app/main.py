from random import randrange
import psycopg # type: ignore
import time
from fastapi import FastAPI, Response, HTTPException, status, Depends # type: ignore
from sqlmodel import Session,SQLModel, select
from . database import get_db, engine
from . import models, schemas, utils
from .routers import post, user, auth

SQLModel.metadata.create_all(engine)

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

while True:
    try:
        conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='123456', port='5432', row_factory=psycopg.rows.dict_row)
        cur = conn.cursor()
        print("Database connection successful")
        break
    except Exception as e:
        print("Database connection failed")
        print("Error:", e)
        time.sleep(2)

@app.get("/")
async def root():
    return {"message": "Welcome to my api!"}