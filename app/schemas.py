from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, ConfigDict

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    is_admin: Optional[bool] = False

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatar: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    registered_at: datetime
    is_verified_author: bool
    is_admin: bool
    avatar: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    is_verified_author: Optional[bool] = None

class NewsCreate(BaseModel):
    title: str
    content: Any
    cover: Optional[str] = None

class NewsRead(BaseModel):
    id: int
    title: str
    content: Any
    published_at: datetime
    author_id: int
    cover: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class CommentCreate(BaseModel):
    text: str
    news_id: int

class CommentRead(BaseModel):
    id: int
    text: str
    news_id: int
    author_id: int
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SessionInfo(BaseModel):
    id: int
    user_agent: str
    created_at: datetime
    expires_at: datetime
