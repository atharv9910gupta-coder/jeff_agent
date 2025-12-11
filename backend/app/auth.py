from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import JWT_SECRET

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7  # 7 days

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain, hashed) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

