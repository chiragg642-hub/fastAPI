from typing import Optional
from ..database import get_db
from .. import models, schemas, oauth2
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=list[schemas.Post])
async def get_posts(db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cur.execute("SELECT * FROM posts")
    # my_posts = cur.fetchall()
    # print(posts)
    posts = db.exec((select(models.Post)).filter(models.Post.title.contains(search)).limit(limit).offset(skip)).all()
    return posts
    

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post) # type: ignore
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    #cur.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", (post.title, post.content, post.published))
    # new_post = cur.fetchone()
    # conn.commit() 
    new_post = models.Post(owner_id = current_user.id, **post.model_dump())  
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/latest", response_model=schemas.Post)
async def get_latest_post(db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cur.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 1")
    # post = cur.fetchone()
    # return post
    post = db.exec(select(models.Post).order_by(models.Post.created_at.desc()).limit(1)).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found"
        )

    return post

@router.get("/{id}", response_model=schemas.Post)
async def get_post(id: int, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cur.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    # post = cur.fetchone()
    post = db.get(models.Post, id)
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT) # type: ignore
async def delete_post(id: int, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cur.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    # existing_post = cur.fetchone()
    # cur.execute("DELETE FROM posts WHERE id = %s", (str(id),))
    # conn.commit()
    post = db.get(models.Post, id)
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")
    
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
async def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
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

    if post_to_update.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    post_data = post.model_dump(exclude_unset=True)

    for key, value in post_data.items():
        setattr(post_to_update, key, value)

    db.commit()
    db.refresh(post_to_update)

    return post_to_update