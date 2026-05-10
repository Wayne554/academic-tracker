from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

journal_category_association = Table(
    'journal_category',
    Base.metadata,
    Column('journal_id', Integer, ForeignKey('journals.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stars = relationship("UserStar", back_populates="user", cascade="all, delete-orphan")
    reads = relationship("UserRead", back_populates="user", cascade="all, delete-orphan")
    created_categories = relationship("Category", back_populates="created_by_user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_by_user = relationship("User", back_populates="created_categories")
    journals = relationship("Journal", secondary=journal_category_association, back_populates="categories")


class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    openalex_source_id = Column(String, unique=True, index=True, nullable=False)
    issn = Column(String, index=True)
    display_name = Column(String, nullable=False)
    publisher = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    categories = relationship("Category", secondary=journal_category_association, back_populates="journals")
    papers = relationship("Paper", back_populates="journal", cascade="all, delete-orphan")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    openalex_work_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(Text, nullable=False)
    doi = Column(String)
    publication_date = Column(String)
    volume = Column(String)
    issue = Column(String)
    authors = Column(JSON)
    abstract = Column(Text)
    landing_page_url = Column(String)
    journal_id = Column(Integer, ForeignKey('journals.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    journal = relationship("Journal", back_populates="papers")
    stars = relationship("UserStar", back_populates="paper", cascade="all, delete-orphan")
    reads = relationship("UserRead", back_populates="paper", cascade="all, delete-orphan")


class UserStar(Base):
    __tablename__ = "user_stars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    starred_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="stars")
    paper = relationship("Paper", back_populates="stars")


class UserRead(Base):
    __tablename__ = "user_reads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reads")
    paper = relationship("Paper", back_populates="reads")
