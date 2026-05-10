from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from datetime import datetime
import models, schemas
from security import get_password_hash


# ========== 用户 CRUD ==========
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = False):
    hashed_pw = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        is_admin=is_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ========== 期刊 CRUD ==========
def get_journals(db: Session, category: str = None, is_active: bool = None):
    query = db.query(models.Journal)
    if category:
        query = query.filter(models.Journal.category == category)
    if is_active is not None:
        query = query.filter(models.Journal.is_active == is_active)
    return query.order_by(models.Journal.name).all()


def get_journal(db: Session, journal_id: int):
    return db.query(models.Journal).filter(models.Journal.id == journal_id).first()


def create_journal(db: Session, journal: schemas.JournalCreate):
    # 检查是否已存在（通过 openalex_id 或 openalex_issn）
    existing = None
    if journal.openalex_id:
        existing = db.query(models.Journal).filter(
            models.Journal.openalex_id == journal.openalex_id
        ).first()
    
    if not existing and journal.openalex_issn:
        # 如果有 ISSN，也检查一下
        existing = db.query(models.Journal).filter(
            models.Journal.openalex_issn == journal.openalex_issn
        ).first()
    
    if existing:
        # 更新已存在的期刊
        update_data = journal.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # 创建新期刊
        db_journal = models.Journal(**journal.model_dump())
        db.add(db_journal)
        db.commit()
        db.refresh(db_journal)
        return db_journal


def update_journal(db: Session, journal_id: int, journal: schemas.JournalUpdate):
    db_journal = get_journal(db, journal_id)
    if not db_journal:
        return None
    update_data = journal.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_journal, field, value)
    db.commit()
    db.refresh(db_journal)
    return db_journal


def delete_journal(db: Session, journal_id: int):
    db_journal = get_journal(db, journal_id)
    if not db_journal:
        return False
    db.delete(db_journal)
    db.commit()
    return True


def get_journal_categories(db: Session):
    result = db.query(models.Journal.category).distinct().order_by(models.Journal.category).all()
    return [r[0] for r in result]


# ========== 论文 CRUD ==========
def get_papers(db: Session, params: schemas.PaperListParams, user_id: int = None):
    query = db.query(models.Paper).join(models.Journal)

    # 关联用户状态
    if user_id:
        query = query.outerjoin(
            models.UserPaper,
            (models.UserPaper.paper_id == models.Paper.id) & (models.UserPaper.user_id == user_id)
        )

    if params.journal_id:
        query = query.filter(models.Paper.journal_id == params.journal_id)
    if params.category:
        query = query.filter(models.Journal.category == params.category)
    if params.is_starred is not None and user_id:
        query = query.filter(models.UserPaper.is_starred == params.is_starred)
    if params.is_read is not None and user_id:
        query = query.filter(models.UserPaper.is_read == params.is_read)
    if params.search:
        search_term = f"%{params.search}%"
        query = query.filter(
            or_(
                models.Paper.title.ilike(search_term),
                models.Paper.abstract.ilike(search_term),
                models.Paper.authors.ilike(search_term),
            )
        )

    # 排序
    sort_column = getattr(models.Paper, params.sort_by, models.Paper.fetched_at)
    if params.order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    total = query.count()
    papers = query.offset(params.skip).limit(params.limit).all()

    # 附加期刊名称和用户状态
    result = []
    for p in papers:
        journal = db.query(models.Journal).filter(models.Journal.id == p.journal_id).first()
        up = None
        if user_id:
            up = db.query(models.UserPaper).filter(
                models.UserPaper.user_id == user_id,
                models.UserPaper.paper_id == p.id
            ).first()
        result.append({
            "id": p.id,
            "openalex_id": p.openalex_id,
            "journal_id": p.journal_id,
            "journal_name": journal.name if journal else "",
            "title": p.title,
            "authors": p.authors,
            "abstract": p.abstract,
            "publication_date": p.publication_date,
            "volume": p.volume,
            "issue": p.issue,
            "pages": p.pages,
            "url": p.url,
            "doi": p.doi,
            "is_read": up.is_read if up else False,
            "is_starred": up.is_starred if up else False,
            "fetched_at": p.fetched_at,
        })
    return result, total


def get_paper(db: Session, paper_id: int, user_id: int = None):
    return db.query(models.Paper).filter(models.Paper.id == paper_id).first()


def create_paper(db: Session, paper_data: dict):
    # 检查是否已存在
    if paper_data.get("openalex_id"):
        existing = db.query(models.Paper).filter(
            models.Paper.openalex_id == paper_data["openalex_id"]
        ).first()
        if existing:
            return existing

    db_paper = models.Paper(**paper_data)
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper


# ========== 用户论文操作 ==========
def update_user_paper(db: Session, user_id: int, paper_id: int, update: schemas.UserPaperUpdate):
    up = db.query(models.UserPaper).filter(
        models.UserPaper.user_id == user_id,
        models.UserPaper.paper_id == paper_id
    ).first()

    now = datetime.utcnow()
    data = update.model_dump(exclude_unset=True)

    if not up:
        up = models.UserPaper(user_id=user_id, paper_id=paper_id)
        db.add(up)
        # 需要刷新以获取ID，但先处理字段

    for field, value in data.items():
        setattr(up, field, value)
        if field == "is_starred" and value:
            up.starred_at = now
        if field == "is_read" and value:
            up.read_at = now

    db.commit()
    db.refresh(up)
    return up


def get_starred_papers(db: Session, user_id: int):
    return db.query(models.Paper).join(models.UserPaper).filter(
        models.UserPaper.user_id == user_id,
        models.UserPaper.is_starred == True
    ).order_by(desc(models.UserPaper.starred_at)).all()
