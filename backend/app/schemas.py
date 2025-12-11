# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    user_id: int

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool
    created_at: datetime
    class Config:
        orm_mode = True

class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TicketOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    owner_id: int
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    role: str
    content: str
    ticket_id: Optional[int] = None

