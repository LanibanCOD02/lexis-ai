from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    role: str = "Lawyer"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
