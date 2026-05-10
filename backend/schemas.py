from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class JournalBase(BaseModel):
    openalex_source_id: str
    issn: Optional[str] = None
    display_name: str
    publisher: Optional[str] = None


class JournalCreate(JournalBase):
    category_ids: Optional[List[int]] = None


class Journal(JournalBase):
    id: int
    created_at: datetime
    categories: List[Category] = []

    model_config = {
        "from_attributes": True
    }


class PaperBase(BaseModel):
    openalex_work_id: str
    title: str
    doi: Optional[str] = None
    publication_date: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    authors: Optional[List[Any]] = None
    abstract: Optional[str] = None
    landing_page_url: Optional[str] = None


class PaperCreate(PaperBase):
    journal_id: int


class Paper(PaperBase):
    id: int
    journal_id: int
    created_at: datetime
    journal: Optional[Journal] = None
    is_starred: Optional[bool] = False
    is_read: Optional[bool] = False

    model_config = {
        "from_attributes": True
    }


class PaperWithDetails(Paper):
    pass
