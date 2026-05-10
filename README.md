# Academic Tracker 📚

个人学术期刊追踪器，帮助研究者追踪 OBHRM 及相关领域顶刊最新论文。

## 功能特性

- 🔐 账号及权限管理（JWT 认证，管理员/普通用户）
- 📂 通过 OpenAlex API 添加和抓取学术期刊
- 🏷️ 自定义期刊分类（战略管理、HRM、AI&人机协同等）
- 📋 层级化论文列表（标题/卷名/作者/摘要）
- 🔗 点击跳转至 Wiley / ScienceDirect 等期刊页面
- ⭐ 星标论文、已读/未读标记
- 📌 独立的星标论文页面

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Vue Router + Pinia + Axios |
| 后端 | Python + FastA |
| 数据库 | SQLite（开发）/ PostgreSQL（生产可选） |
| 数据源 | OpenAlex API（免费，无需 Key） |

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # 修改 SECRET_KEY 和管理员密码
python init_db.py       # 初始化数据库和管理员账号
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`，使用初始账号登录（见 `.env` 配置）。

## 添加期刊

1. 登录后进入「期刊管理」
2. 填写期刊名称和 OpenAlex ISSN（可在 [openalex.org](https://openalex.org) 查询）
3. 设置分类（如 `HRM`、`战略管理`、`AI与心理学`）
4. 保存后，到服务器运行 `python fetch_papers.py` 抓取论文

## 部署

后端运行在 `119.28.14.122:8000`，前端 build 后通过 Nginx 反代：
```bash
# 前端构建
cd frontend && npm run build
# 将 dist/ 目录部署到服务器
```
