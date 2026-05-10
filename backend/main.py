from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, journals, papers
from database import engine, init_db
import models

app = FastAPI(title="Academic Tracker API", version="1.0.0")

# CORS 配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请改为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(journals.router)
app.include_router(papers.router)


@app.on_event("startup")
def startup():
    # 初始化数据库（含默认管理员账号）
    init_db()
    # 触发一次期刊和论文抓取（可注释掉，改为手动触发）
    # from fetch_papers import fetch_all_journals
    # fetch_all_journals()


@app.get("/")
def root():
    return {"msg": "Academic Tracker API is running"}
