from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    openalex_issn = Column(String(20), unique=True, nullable=True, index=True)  # OpenAlex ISSN
    name = Column(String(255), nullable=False)
    publisher = Column(String(255), nullable=True)
    category = Column(String(100), nullable=False, index=True)  # 自定义分类
    url = Column(String(500), nullable=True)  # 期刊主页/投稿页
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    openalex_id = Column(String(50), unique=True, nullable=True, index=True)
    journal_id = Column(Integer, ForeignKey("journals.id"), nullable=False)
    title = Column(Text, nullable=False)
    authors = Column(Text, nullable=True)  # JSON string
    abstract = Column(Text, nullable=True)
    publication_date = Column(String(20), nullable=True)
    volume = Column(String(50), nullable=True)
    issue = Column(String(50), nullable=True)
    pages = Column(String(50), nullable=True)
    url = Column(String(500), nullable=True)  # 跳转链接（Wiley/ScienceDirect等）
    doi = Column(String(200), nullable=True)
    is_read = Column(Boolean, default=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("journal_id", "openalex_id", name="uq_journal_paper"),)


class UserPaper(Base):
    """用户与论文的关联表（星标、已读状态）"""
    __tablename__ = "user_papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    is_starred = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    starred_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "paper_id", name="uq_user_paper"),)
