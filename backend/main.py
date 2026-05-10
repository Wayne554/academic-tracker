from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from database import engine, SessionLocal, get_db
import models
import schemas
import crud
import auth
from auth import settings
from openalex import search_journals

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Academic Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_admin():
    db = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        existing = crud.get_user_by_email(db, admin_email)
        if not existing:
            admin_create = schemas.UserCreate(email=admin_email, password=admin_password)
            crud.create_user(db, admin_create, is_admin=True)
            print(f"管理员账户已创建: {admin_email}")
    finally:
        db.close()


init_admin()


@app.get("/")
async def read_root():
    frontend_path = Path("frontend/dist/index.html")
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {"message": "Academic Tracker API"}


@app.post("/api/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    return current_user


@app.get("/api/users", response_model=List[schemas.User])
async def get_users(db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_admin_user)):
    return crud.get_users(db)


@app.post("/api/users", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_admin_user)):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="邮箱已注册")
    return crud.create_user(db, user, is_admin=False)


@app.get("/api/categories", response_model=List[schemas.Category])
async def get_categories(db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_current_active_user)):
    return crud.get_categories(db)


@app.post("/api/categories", response_model=schemas.Category)
async def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_admin_user)):
    return crud.create_category(db, category, current_user.id)


@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_admin_user)):
    success = crud.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"message": "删除成功"}


@app.put("/api/categories/{category_id}", response_model=schemas.Category)
async def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_admin_user)):
    updated = crud.update_category(db, category_id, category.name)
    if not updated:
        raise HTTPException(status_code=404, detail="分类不存在")
    return updated


@app.get("/api/journals", response_model=List[schemas.Journal])
async def get_journals(db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_current_active_user)):
    return crud.get_journals(db)


@app.post("/api/journals", response_model=schemas.Journal)
async def create_journal(journal: schemas.JournalCreate, db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_admin_user)):
    return crud.create_journal(db, journal)


@app.delete("/api/journals/{journal_id}")
async def delete_journal(journal_id: int, db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_admin_user)):
    success = crud.delete_journal(db, journal_id)
    if not success:
        raise HTTPException(status_code=404, detail="期刊不存在")
    return {"message": "删除成功"}


@app.get("/api/openalex/search")
async def search_openalex_journals(query: str, _: schemas.User = Depends(auth.get_admin_user)):
    results = search_journals(query)
    return {"results": results}


@app.get("/api/papers")
async def get_papers(
    journal_id: Optional[int] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    starred_only: bool = False,
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    papers, total = crud.get_papers(
        db,
        journal_id=journal_id,
        category_id=category_id,
        search=search,
        sort=sort,
        user_id=current_user.id,
        starred_only=starred_only,
        unread_only=unread_only,
        skip=skip,
        limit=limit
    )
    return {
        "papers": papers,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@app.post("/api/papers/{paper_id}/star")
async def star_paper(paper_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    is_starred = crud.toggle_star(db, current_user.id, paper_id)
    return {"starred": is_starred}


@app.post("/api/papers/{paper_id}/read")
async def mark_paper_read(paper_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    crud.mark_read(db, current_user.id, paper_id)
    return {"message": "已标记为已读"}


@app.post("/api/admin/refresh")
async def refresh_all(db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_admin_user)):
    new_count = crud.refresh_all_papers(db)
    return {"new_papers": new_count}


@app.post("/api/journals/{journal_id}/refresh")
async def refresh_journal(journal_id: int, db: Session = Depends(get_db), _: schemas.User = Depends(auth.get_admin_user)):
    new_count = crud.refresh_journal_papers(db, journal_id)
    return {"new_papers": new_count}


# 注意：静态文件现在由 Nginx 处理，这里不需要了
# 但我们保留一个健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
