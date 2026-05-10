from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


# ========== 用户相关 ==========
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== Token ==========
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ========== 期刊相关 ==========
class JournalBase(BaseModel):
    name: str
    category: str
    openalex_issn: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None


class JournalCreate(JournalBase):
    pass


class JournalUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    openalex_issn: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None


class JournalOut(JournalBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 论文相关 ==========
class PaperBase(BaseModel):
    title: str
    authors: Optional[str] = None
    abstract: Optional[str] = None
    publication_date: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None


class PaperOut(PaperBase):
    id: int
    openalex_id: Optional[str] = None
    journal_id: int
    journal_name: Optional[str] = None
    is_read: bool = False
    is_starred: bool = False
    fetched_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaperListParams(BaseModel):
    journal_id: Optional[int] = None
    category: Optional[str] = None
    is_starred: Optional[bool] = None
    is_read: Optional[bool] = None
    search: Optional[str] = None
    sort_by: str = "fetched_at"
    order: str = "desc"
    skip: int = 0
    limit: int = 50


# ========== 用户论文操作 ==========
class UserPaperUpdate(BaseModel):
    is_starred: Optional[bool] = None
    is_read: Optional[bool] = None
