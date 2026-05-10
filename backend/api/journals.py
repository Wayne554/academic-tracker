from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
from .auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/journals", tags=["期刊管理"])


@router.get("", response_model=list[schemas.JournalOut])
def list_journals(
    category: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return crud.get_journals(db, category=category, is_active=is_active)


@router.get("/categories")
def list_categories(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return {"categories": crud.get_journal_categories(db)}


@router.get("/{journal_id}", response_model=schemas.JournalOut)
def get_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    journal = crud.get_journal(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="期刊不存在")
    return journal


@router.post("", response_model=schemas.JournalOut)
def create_journal(
    journal: schemas.JournalCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return crud.create_journal(db, journal)


@router.put("/{journal_id}", response_model=schemas.JournalOut)
def update_journal(
    journal_id: int,
    journal: schemas.JournalUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    result = crud.update_journal(db, journal_id, journal)
    if not result:
        raise HTTPException(status_code=404, detail="期刊不存在")
    return result


@router.delete("/{journal_id}")
def delete_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    ok = crud.delete_journal(db, journal_id)
    if not ok:
        raise HTTPException(status_code=404, detail="期刊不存在")
    return {"msg": "删除成功"}
