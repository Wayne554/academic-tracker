# Changelog

## [1.1.0] - 2026-05-10 - OpenAlex 期刊搜索集成

### 新增功能
- ✅ **OpenAlex 期刊搜索功能**
  - 后端新增 `/api/openalex/search` 接口，通过 OpenAlex API 搜索期刊
  - 后端新增 `/api/openalex/{journal_id}` 接口，获取期刊详细信息
  - 前端新增 `JournalSearch.vue` 组件，支持搜索并选择期刊
  - 在期刊管理页面集成 OpenAlex 搜索功能

### 技术细节
- **后端（FastAPI）**：
  - 新增 `backend/openalex.py`，使用 httpx 调用 OpenAlex API
  - 修改 `backend/main.py`，注册 OpenAlex 路由，API 版本升级至 v1.1.0
  - 搜索参数：`query`（期刊名称）、`limit`（结果数量，默认 10）
  - 返回数据：期刊名称、ISSN、出版社、论文数、被引次数、主页 URL、OpenAlex ID

- **前端（Vue.js）**：
  - 新增 `frontend/src/components/JournalSearch.vue` 组件
  - 修改 `frontend/src/views/JournalManageView.vue`，集成搜索组件
  - 选择期刊后自动填充表单（名称、出版社、ISSN、URL）
  - 使用 Emoji 作为图标（无需额外依赖）

### 使用方法
1. 进入"期刊管理"页面
2. 在页面顶部输入期刊英文名称（如 "Journal of Applied Psychology"）
3. 点击"搜索"按钮
4. 从搜索结果中点击选择期刊
5. 表单会自动填充期刊信息
6. 补充其他必要信息（如分类）
7. 点击"添加期刊"按钮

### 优势
- ✅ **准确性**：通过 OpenAlex 官方数据，避免拼写错误
- ✅ **完整性**：自动获取 ISSN、出版社、主页等信息
- ✅ **便捷性**：无需手动查找期刊主页 URL
- ✅ **标准化**：使用 OpenAlex ID 作为唯一标识

### 依赖变更
- ✅ `httpx==0.27.2`（已在 requirements.txt 中）

### Bug 修复
- 无

### 已知问题
- 需要网络连接以访问 OpenAlex API（https://api.openalex.org）
- 搜索结果限制为 10 条（可在前端修改 `limit` 参数增加）

---

## [1.0.0] - 2026-05-10 - 初始版本

### 新增功能
- ✅ 用户登录/注册功能（JWT 认证）
- ✅ 期刊管理（添加、编辑、删除）
- ✅ 论文列表展示
- ✅ 期刊分类筛选
- ✅ 论文星标收藏功能

### 技术栈
- **后端**：FastAPI + SQLAlchemy + SQLite
- **前端**：Vue.js + Vite
- **部署**：Caddy 反向代理

---

## 版本号说明
- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正
