from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, schemas, security
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    return crud.create_user(db, user, is_admin=False)


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = security.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token = security.create_access_token(data={"sub": user.username, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: schemas.UserOut = Depends(get_current_user)):
    return current_user


# ========== 依赖注入：获取当前用户 ==========
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = security.decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效")
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效")
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return schemas.UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def get_current_admin(
    current_user: schemas.UserOut = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user
