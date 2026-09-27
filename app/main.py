from typing import Optional
from random import randrange
import psycopg # type: ignore
import time

from fastapi import FastAPI, Response, HTTPException, status, Depends # type: ignore
from pydantic import BaseModel
from sqlmodel import Session,SQLModel, select
from . database import get_db, engine
from . import models

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

app = FastAPI()

SQLModel.metadata.create_all(engine)

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


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):

    posts = db.exec(select(models.Post)).all()

    return {"data": posts}

@app.get("/")
async def root():
    return {"message": "Welcome to my api!"}

@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    # cur.execute("SELECT * FROM posts")
    # my_posts = cur.fetchall()
    # print(posts)
    posts = db.exec(select(models.Post)).all()
    return {"data": posts}
    

@app.post("/posts", status_code=status.HTTP_201_CREATED) # type: ignore
async def create_posts(post: Post, db: Session = Depends(get_db)):
    #cur.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", (post.title, post.content, post.published))
    # new_post = cur.fetchone()
    # conn.commit() 
    new_post = models.Post(**post.model_dump())  
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"Data": new_post}

@app.get("/posts/latest")
async def get_latest_post():
    cur.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 1")
    post = cur.fetchone()
    return {"latest_post": post}

@app.get("/posts/{id}")
async def get_post(id: int, db: Session = Depends(get_db)):
    # cur.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    # post = cur.fetchone()
    post = db.get(models.Post, id)
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT) # type: ignore
async def delete_post(id: int, db: Session = Depends(get_db)):
    # cur.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    # existing_post = cur.fetchone()
    # cur.execute("DELETE FROM posts WHERE id = %s", (str(id),))
    # conn.commit()
    post = db.get(models.Post, id)
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} does not exist")

    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
async def update_post(id: int, post: Post, db: Session = Depends(get_db)):
    # cur.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    # existing_post = cur.fetchone()
    # if not existing_post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")

    # cur.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", (post.title, post.content, post.published, str(id)))
    # updated_post = cur.fetchone()
    # conn.commit()
    post_to_update = db.get(models.Post, id)

    if not post_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found"
        )

    post_data = post.model_dump(exclude_unset=True)

    for key, value in post_data.items():
        setattr(post_to_update, key, value)

    db.commit()
    db.refresh(post_to_update)

    return {"updated_post": post_to_update}