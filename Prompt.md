你是一位资深全栈工程师，请用 Python FastAPI + React + SQLite + Docker 开发一个**个人学术期刊追踪网站**，项目名为 `academic-tracker`，并配置 GitHub Actions 自动部署到腾讯云轻量服务器 (IP: 119.28.14.122)。请输出**完整项目目录结构和每个文件代码**。

## 1. 项目目标

替代 Chrome 的 Feedbro Reader 插件，专注追踪 OBHRM（组织行为与人力资源管理）和心理学×AI 交叉领域的顶刊论文。网站仅限授权用户使用，界面响应式、操作无延迟感。

## 2. 核心功能要求

### 2.1 用户与权限

- 仅管理员可登录后台添加/管理其他用户（无公开注册）。
- 所有用户需登录后才能访问页面。
- 管理员可：添加期刊、管理分类、拉取最新论文。
- 普通用户可：浏览、搜索、星标、标记已读/未读。
- 首次启动时自动创建管理员账户（邮箱和密码通过环境变量 `ADMIN_EMAIL` / `ADMIN_PASSWORD` 设置）。

### 2.2 添加期刊

- 管理员在界面输入期刊名/ISSN，调用 **OpenAlex API** `https://api.openalex.org/sources?search=...` 实时搜索期刊。
- 展示匹配的期刊列表，用户点击“添加”将其存入数据库。
- 添加时可选择一个或多个自定义分类（分类由管理员维护，支持增删改）。

### 2.3 自定义分类

- 管理员可创建/编辑/删除分类，如：“战略管理”、“组织与变革”、“HRM”、“应用心理学”、“AI & 人机协同”。
- 期刊与分类多对多关系。

### 2.4 获取最新论文

- 首先支持在添加的期刊页面点击特定按钮进行最新论文的刷新；
- 如果API允许且不会触发cloudflare等反爬机制，后端定时任务（每6小时）遍历所有已关注期刊的 OpenAlex source ID，调用 `https://api.openalex.org/works?filter=primary_location.source.id:SOURCE_ID&sort=publication_date:desc&per_page=50`。
- 提取字段：`id` (OpenAlex work ID), `title`, `doi`, `publication_date`, `primary_location.landing_page_url`, `authorships`, `biblio` (volume/issue), `abstract_inverted_index`。
- **重要**：需将 `abstract_inverted_index` 重建为纯文本摘要并存储。
- 根据 work ID 去重，仅入库新论文。

### 2.5 论文展示与交互

- 以列表形式展示论文，字段：标题、期刊名、卷/期、作者、日期、摘要前200字、原文链接（使用 `landing_page_url` 或 `https://doi.org/DOI`）。
- 支持按期刊、分类、日期筛选；支持标题搜索。
- 多种排序：发布日期、期刊名、标题。
- 每条论文可点击星标（★）、标记已读/未读（蓝色圆点），状态与登录用户绑定。
- 顶部导航栏包含“Starred Items”独立页面，显示当前用户所有星标论文，支持取消星标。
- 点击标题或链接按钮可在新标签页打开原文。

### 2.6 界面与体验

- 左侧边栏：分类树 + 期刊列表（可折叠），点击分类过滤论文。
- 主区域：论文列表，每项可展开查看完整摘要。
- 右上角用户菜单：显示邮箱，登出。
- 管理员专有入口：管理期刊、管理分类、管理用户。
- 所有操作通过 AJAX 完成，无整页刷新，响应时间 < 300ms。

## 3. 技术栈与架构

- **后端**：Python 3.11+ FastAPI，JWT 鉴权，SQLite（文件 `data.db`），APScheduler 定时拉取。
- **前端**：React 18 (使用 Vite)，React Router v6，状态管理用 Context 或 zustand，Tailwind CSS，axios。
- **打包**：多阶段 Docker 构建。第一阶段构建 React 静态文件，第二阶段将这些文件复制到 FastAPI 容器内并由 FastAPI 挂载静态目录，提供全栈服务。最终只运行一个容器，监听 8000 端口。
- **反向代理**：可选，Docker 直接暴露 8000，后续可加 Nginx。暂时不需要在代码中实现 HTTPS，仅 HTTP。

## 4. 数据库模型 (SQLAlchemy)

- `User`: id, email, password_hash, is_admin (bool), created_at
- `Category`: id, name, created_by (user_id)
- `Journal`: id, openalex_source_id (unique), issn, display_name, publisher, created_at
- `journal_category` 关联表（journal_id, category_id）
- `Paper`: id, openalex_work_id (unique), title, doi, publication_date, volume, issue, authors (JSON), abstract (text), landing_page_url, journal_id, created_at
- `UserStar`: id, user_id, paper_id, starred_at
- `UserRead`: id, user_id, paper_id, read_at

## 5. API 端点概要

- `POST /api/auth/login` , `/logout` , `GET /api/auth/me`
- `GET /api/journals` , `POST /api/journals` (管理员, 传入 openalex_source_id, category_ids)
- `GET /api/categories` , `POST /api/categories` , `DELETE /api/categories/{id}` (管理员)
- `GET /api/papers`  (支持查询参数: `journal_id`, `category_id`, `search`, `sort`, `starred_only` 仅当前用户, `unread_only` 等)
- `POST /api/papers/{id}/star` , `DELETE /api/papers/{id}/star`
- `POST /api/papers/{id}/read` (标记已读)
- `GET /api/users` (管理员), `POST /api/users` (管理员添加用户)
- `POST /api/admin/refresh` (手动触发拉取)

## 6. 定时任务（可选，优先确保按钮手动刷新）

- 使用 APScheduler，在应用启动后每 6 小时运行一次 `update_all_papers()`：遍历所有 Journal，调用 OpenAlex API，存入新 Paper。

## 7. 自动化部署 (GitHub Actions + Docker)

- 项目根目录提供 `Dockerfile`, `docker-compose.yml`, `.github/workflows/deploy.yml`。
- `docker-compose.yml` 内定义服务 `app`，映射端口 `8000:8000`，挂载 `./data` 目录以持久化 SQLite。
- GitHub Actions 触发条件：push 到 `main` 分支。
- 流程步骤：
  1. Checkout 代码。
  2. 使用 `appleboy/ssh-action` 通过 SSH 连接服务器 `119.28.14.122`。
  3. 执行远程脚本：`cd /home/your-user/journal-tracker && git pull origin main && echo "ADMIN_EMAIL=${{ secrets.ADMIN_EMAIL }}" > .env && echo "ADMIN_PASSWORD=${{ secrets.ADMIN_PASSWORD }}" >> .env && echo "JWT_SECRET=${{ secrets.JWT_SECRET }}" >> .env && docker compose up -d --build`
- 请在 README 中写明：需要在服务器首次克隆仓库，创建 `/home/your-user/journal-tracker` 目录，并设置好 GitHub 仓库的 Secrets（`SERVER_HOST`, `SERVER_USER`, `SSH_PRIVATE_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `JWT_SECRET`）。以后只需本地推送代码，GitHub 自动部署，无需在服务器上修改代码。

## 8. 额外要求

- 代码必须有良好的注释，方便非程序员理解。
- 提供 `.env.example` 以及详细的 `README.md`，包含初始部署步骤。
- 所有前端的 API 请求需携带 JWT (存储于 localStorage)，后端验证所有受限端点。
- 前端实现加载骨架屏或微调器，提升感知性能。
- 移动端布局自适应。

请按以上要求生成完整项目代码，确保可一键 `docker compose up` 运行。
