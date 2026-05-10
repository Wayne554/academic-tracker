from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
from .auth import get_current_user

router = APIRouter(prefix="/api/papers", tags=["论文管理"])


@router.get("", response_model=list[dict])
def list_papers(
    journal_id: int = None,
    category: str = None,
    is_starred: bool = None,
    is_read: bool = None,
    search: str = None,
    sort_by: str = "fetched_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    params = schemas.PaperListParams(
        journal_id=journal_id,
        category=category,
        is_starred=is_starred,
        is_read=is_read,
        search=search,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )
    papers, total = crud.get_papers(db, params, user_id=user.id)
    return papers


@router.get("/starred", response_model=list[dict])
def list_starred(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    papers = crud.get_starred_papers(db, user.id)
    return [{
        "id": p.id,
        "title": p.title,
        "authors": p.authors,
        "journal_name": crud.get_journal(db, p.journal_id).name if crud.get_journal(db, p.journal_id) else "",
        "publication_date": p.publication_date,
        "url": p.url,
        "doi": p.doi,
    } for p in papers]


@router.patch("/{paper_id}", response_model=dict)
def update_paper_status(
    paper_id: int,
    update: schemas.UserPaperUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # 先确认论文存在
    paper = crud.get_paper(db, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在")
    up = crud.update_user_paper(db, user.id, paper_id, update)
    return {
        "msg": "更新成功",
        "is_starred": up.is_starred,
        "is_read": up.is_read,
    }


@router.get("/{paper_id}")
def get_paper_detail(
    paper_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    paper = crud.get_paper(db, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在")
    journal = crud.get_journal(db, paper.journal_id)
    up = db.query(crud.models.UserPaper).filter(
        crud.models.UserPaper.user_id == user.id,
        crud.models.UserPaper.paper_id == paper.id
    ).first()
    return {
        "id": paper.id,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "publication_date": paper.publication_date,
        "volume": paper.volume,
        "issue": paper.issue,
        "pages": paper.pages,
        "url": paper.url,
        "doi": paper.doi,
        "journal_name": journal.name if journal else "",
        "is_read": up.is_read if up else False,
        "is_starred": up.is_starred if up else False,
    }
