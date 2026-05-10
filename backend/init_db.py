"""
数据库初始化脚本：
1. 创建所有表
2. 创建默认管理员账号（从 .env 读取账号密码）
运行：python init_db.py
"""
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal, init_db
from . import models, crud, security
from .config import get_settings


def init_database():
    settings = get_settings()
    # 1. 创建所有表
    Base.metadata.create_all(bind=engine)
    print("[OK] 数据库表创建完成")

    # 2. 创建默认管理员
    db = SessionLocal()
    try:
        admin = crud.get_user_by_username(db, settings.INIT_ADMIN_USERNAME)
        if not admin:
            admin = models.User(
                username=settings.INIT_ADMIN_USERNAME,
                email=settings.INIT_ADMIN_EMAIL,
                hashed_password=security.get_password_hash(settings.INIT_ADMIN_PASSWORD),
                is_admin=True,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"[OK] 默认管理员账号已创建：{settings.INIT_ADMIN_USERNAME} / {settings.INIT_ADMIN_PASSWORD}")
            print("  ⚠️  请登录后立即修改密码！")
        else:
            print(f"[SKIP] 管理员账号已存在：{settings.INIT_ADMIN_USERNAME}")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
