# app/auth.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings
from app import schemas

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_ctx.verify(password, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return schemas.TokenPayload(user_id=payload.get("user_id"))
    except JWTError:
        return None
