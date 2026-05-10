from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from models import User, Category, Journal, Paper, UserStar, UserRead
from schemas import UserCreate, CategoryCreate, JournalCreate, PaperCreate
from auth import get_password_hash
from openalex import fetch_papers_from_journal


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate, is_admin: bool = False):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_categories(db: Session):
    return db.query(Category).all()


def create_category(db: Session, category: CategoryCreate, created_by: int):
    db_category = Category(name=category.name, created_by=created_by)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        db.delete(category)
        db.commit()
        return True
    return False


def update_category(db: Session, category_id: int, new_name: str):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        category.name = new_name
        db.commit()
        db.refresh(category)
        return category
    return None


def get_journals(db: Session):
    return db.query(Journal).all()


def get_journal(db: Session, journal_id: int):
    return db.query(Journal).filter(Journal.id == journal_id).first()


def create_journal(db: Session, journal: JournalCreate):
    db_journal = Journal(
        openalex_source_id=journal.openalex_source_id,
        issn=journal.issn,
        display_name=journal.display_name,
        publisher=journal.publisher
    )
    if journal.category_ids:
        categories = db.query(Category).filter(Category.id.in_(journal.category_ids)).all()
        db_journal.categories = categories
    db.add(db_journal)
    db.commit()
    db.refresh(db_journal)
    return db_journal


def delete_journal(db: Session, journal_id: int):
    journal = db.query(Journal).filter(Journal.id == journal_id).first()
    if journal:
        db.delete(journal)
        db.commit()
        return True
    return False


def get_papers(
    db: Session,
    journal_id: Optional[int] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    user_id: Optional[int] = None,
    starred_only: bool = False,
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50
):
    query = db.query(Paper)

    if journal_id:
        query = query.filter(Paper.journal_id == journal_id)

    if category_id:
        query = query.join(Journal).join(Journal.categories).filter(Category.id == category_id)

    if search:
        query = query.filter(Paper.title.ilike(f"%{search}%"))

    if sort == "date":
        query = query.order_by(Paper.publication_date.desc())
    elif sort == "journal":
        query = query.join(Journal).order_by(Journal.display_name, Paper.publication_date.desc())
    elif sort == "title":
        query = query.order_by(Paper.title)
    else:
        query = query.order_by(Paper.publication_date.desc())

    if starred_only and user_id:
        query = query.join(UserStar).filter(UserStar.user_id == user_id)

    if unread_only and user_id:
        query = query.outerjoin(UserRead, and_(UserRead.paper_id == Paper.id, UserRead.user_id == user_id)).filter(UserRead.id.is_(None))

    total = query.count()
    papers = query.offset(skip).limit(limit).all()

    if user_id:
        for paper in papers:
            star = db.query(UserStar).filter(UserStar.user_id == user_id, UserStar.paper_id == paper.id).first()
            paper.is_starred = star is not None
            read = db.query(UserRead).filter(UserRead.user_id == user_id, UserRead.paper_id == paper.id).first()
            paper.is_read = read is not None

    return papers, total


def create_paper(db: Session, paper: PaperCreate):
    db_paper = Paper(
        openalex_work_id=paper.openalex_work_id,
        title=paper.title,
        doi=paper.doi,
        publication_date=paper.publication_date,
        volume=paper.volume,
        issue=paper.issue,
        authors=paper.authors,
        abstract=paper.abstract,
        landing_page_url=paper.landing_page_url,
        journal_id=paper.journal_id
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper


def get_paper_by_openalex_id(db: Session, openalex_work_id: str):
    return db.query(Paper).filter(Paper.openalex_work_id == openalex_work_id).first()


def toggle_star(db: Session, user_id: int, paper_id: int):
    star = db.query(UserStar).filter(UserStar.user_id == user_id, UserStar.paper_id == paper_id).first()
    if star:
        db.delete(star)
        db.commit()
        return False
    else:
        new_star = UserStar(user_id=user_id, paper_id=paper_id)
        db.add(new_star)
        db.commit()
        return True


def mark_read(db: Session, user_id: int, paper_id: int):
    read = db.query(UserRead).filter(UserRead.user_id == user_id, UserRead.paper_id == paper_id).first()
    if not read:
        new_read = UserRead(user_id=user_id, paper_id=paper_id)
        db.add(new_read)
        db.commit()
    return True


def refresh_journal_papers(db: Session, journal_id: int):
    journal = get_journal(db, journal_id)
    if not journal:
        return 0

    papers = fetch_papers_from_journal(journal.openalex_source_id)
    new_count = 0

    for paper_data in papers:
        existing = get_paper_by_openalex_id(db, paper_data["openalex_work_id"])
        if not existing:
            paper_create = PaperCreate(**paper_data, journal_id=journal.id)
            create_paper(db, paper_create)
            new_count += 1

    return new_count


def refresh_all_papers(db: Session):
    journals = get_journals(db)
    total_new = 0
    for journal in journals:
        new_count = refresh_journal_papers(db, journal.id)
        total_new += new_count
    return total_new
