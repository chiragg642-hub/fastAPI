from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlmodel import Session, select
from .. import models, schemas, utils, database

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.exec(select(models.User).where(models.User.email == user_credentials.email)).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    return {"message": "Login successful"}