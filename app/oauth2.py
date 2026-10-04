from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session
from . import schemas, database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Placeholder for OAuth2PasswordBearer or similar dependency

SECRET_KEY = "4fb46c2dc1bdb617532a1dc1c0a0ffd0269ceab3854885f14c50e432ce06f799"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise ValueError("Invalid token: user_id not found")
        token_data = schemas.TokenData(id=user_id)
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


    return verify_access_token(token, credentials_exception)