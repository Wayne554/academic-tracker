# Academic Tracker

个人学术期刊追踪系统，专注于 OBHRM（组织行为与人力资源管理）和心理学×AI 交叉领域的顶刊论文追踪。

## 功能特性

- 用户认证与权限管理（仅管理员可添加用户）
- 通过 OpenAlex API 搜索和添加期刊
- 期刊分类管理
- 论文拉取与更新
- 论文浏览、搜索、筛选和排序
- 星标论文和已读标记
- 响应式设计，支持移动端
- Docker 容器化部署
- GitHub Actions 自动部署

## 技术栈

- 后端：Python 3.11+, FastAPI, SQLAlchemy, SQLite
- 前端：React 18, Vite, Tailwind CSS, Zustand
- 部署：Docker, GitHub Actions

## 快速开始

### 本地开发（已成功测试）

**Windows 用户**：
```bash
# 终端 1 - 启动后端
start-backend.bat

# 终端 2 - 启动前端
start-frontend.bat
```

**所有平台手动运行**：
```bash
# 终端 1 - 后端
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2 - 前端
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### 默认登录信息

- 邮箱：`admin@example.com`
- 密码：`admin123`

### 使用说明

1. **首次登录后，进入"管理后台"**
2. **添加分类**，如 "战略管理"、"HRM" 等
3. **搜索并添加期刊**（使用 OpenAlex API）
4. **刷新期刊论文**（手动或定时）
5. **开始浏览论文**！

### Docker 部署

```bash
cp .env.example .env
# 编辑 .env 文件
docker compose up -d --build
```

访问 http://localhost:8000

## 服务器部署

### 初始服务器设置

1. 在服务器上克隆仓库：

```bash
cd /home/ubuntu
git clone <your-repo-url> academic-tracker
cd academic-tracker
```

2. 创建 `.env` 文件（首次手动创建）

3. 配置 GitHub Secrets：

在 GitHub 仓库的 Settings → Secrets and variables → Actions 中添加以下 secrets：

- `SERVER_HOST`: 服务器 IP 地址 (119.28.14.122)
- `SERVER_USER`: 服务器用户名 (ubuntu)
- `SSH_PRIVATE_KEY`: 服务器 SSH 私钥
- `ADMIN_EMAIL`: 管理员邮箱
- `ADMIN_PASSWORD`: 管理员密码
- `SECRET_KEY`: JWT 密钥（可以用 `openssl rand -hex 32` 生成）

### 自动部署

推送代码到 `main` 分支后，GitHub Actions 会自动部署到服务器。

## 默认账户

首次启动时会自动创建管理员账户：

- 邮箱：`ADMIN_EMAIL` 环境变量指定（默认：admin@example.com）
- 密码：`ADMIN_PASSWORD` 环境变量指定（默认：admin123）

请务必在生产环境中修改默认密码！

## 项目结构

```
academic-tracker/
├── backend/              # 后端代码
│   ├── main.py          # FastAPI 主应用
│   ├── models.py        # SQLAlchemy 模型
│   ├── schemas.py       # Pydantic 模式
│   ├── auth.py          # 认证相关
│   ├── crud.py          # 数据库操作
│   ├── openalex.py      # OpenAlex API 交互
│   └── requirements.txt
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── components/  # React 组件
│   │   ├── pages/       # 页面组件
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── store.js     # Zustand 状态管理
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── data/                # SQLite 数据目录
├── .github/workflows/   # GitHub Actions 配置
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API 端点

- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息
- `GET /api/users` - 获取用户列表（管理员）
- `POST /api/users` - 创建用户（管理员）
- `GET /api/categories` - 获取分类列表
- `POST /api/categories` - 创建分类（管理员）
- `DELETE /api/categories/{id}` - 删除分类（管理员）
- `GET /api/journals` - 获取期刊列表
- `POST /api/journals` - 添加期刊（管理员）
- `DELETE /api/journals/{id}` - 删除期刊（管理员）
- `GET /api/openalex/search` - 搜索 OpenAlex 期刊（管理员）
- `GET /api/papers` - 获取论文列表
- `POST /api/papers/{id}/star` - 星标/取消星标论文
- `POST /api/papers/{id}/read` - 标记论文为已读
- `POST /api/admin/refresh` - 刷新所有期刊论文（管理员）
- `POST /api/journals/{id}/refresh` - 刷新特定期刊论文（管理员）

## 许可证

MIT
