# 部署指南

本指南将帮助您将项目推送到 GitHub 并自动部署到腾讯云服务器。

## 前置条件

- GitHub 账号
- 腾讯云服务器（IP: 119.28.14.122）
- 服务器已安装 Docker 和 Docker Compose

---

## 第一步：创建 GitHub 仓库并推送代码

### 1. 在 GitHub 上创建新仓库
- 访问 https://github.com/new
- 仓库名称：`academic-tracker`（或您喜欢的其他名称）
- 选择 Public 或 Private（建议 Private）
- **不要**初始化 README、.gitignore 或 LICENSE
- 点击 "Create repository"

### 2. 关联远程仓库并推送

```bash
# 替换为您的 GitHub 用户名
git remote add origin https://github.com/[您的用户名]/academic-tracker.git

# 推送到 main 分支
git branch -M main
git push -u origin main
```

---

## 第二步：配置服务器环境

### 1. 登录到腾讯云服务器

```bash
ssh root@119.28.14.122
```

### 2. 确保服务器已安装 Docker 和 Docker Compose

```bash
# 检查 Docker 是否安装
docker --version

# 检查 Docker Compose 是否安装
docker compose version
```

如果未安装，请使用以下命令安装：

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose（如果使用较新版本 Docker，已内置 compose）
# 检查是否有 compose 命令：docker compose version
```

### 3. 创建项目目录

```bash
# 在服务器上创建项目目录
mkdir -p /root/academic-tracker
cd /root/academic-tracker
```

### 4. 创建 .env 文件

```bash
# 创建 .env 文件，替换 SECRET_KEY 为强密码
cat > .env << 'EOF'
SECRET_KEY=your-very-strong-secret-key-change-this-in-production
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
EOF

# 修改 .env 文件权限
chmod 600 .env
```

**注意**：请将 `SECRET_KEY` 替换为足够强的随机字符串！

---

## 第三步：配置 GitHub Secrets

在您的 GitHub 仓库中：

1. 进入 **Settings** -> **Secrets and variables** -> **Actions**
2. 点击 **New repository secret**
3. 添加以下 secrets：

| Secret Name | 说明 | 示例值 |
|-------------|------|--------|
| `HOST` | 服务器 IP | `119.28.14.122` |
| `USERNAME` | SSH 用户名 | `root` |
| `SSH_PRIVATE_KEY` | SSH 私钥 | 见下方说明 |
| `SSH_PORT` | SSH 端口 | `22`（默认） |

### 如何获取 SSH_PRIVATE_KEY

```bash
# 在您的本地电脑上（Windows PowerShell 或终端）

# 如果还没有 SSH 密钥，先生成一个
ssh-keygen -t ed25519 -C "github-deploy@your-server"

# 将公钥添加到服务器（这样我们可以使用 SSH 密钥登录）
ssh-copy-id root@119.28.14.122
# 或者手动将 ~/.ssh/id_ed25519.pub 的内容添加到服务器的 ~/.ssh/authorized_keys 文件

# 复制私钥内容（完整内容，包括 -----BEGIN... 和 -----END...）
cat ~/.ssh/id_ed25519
```

将这个私钥内容完整粘贴到 GitHub 的 `SSH_PRIVATE_KEY` secret 中。

---

## 第四步：第一次手动部署（测试）

在进行自动部署之前，我们先进行一次手动部署来测试：

### 1. 在服务器上克隆仓库

```bash
cd /root/academic-tracker
git clone https://github.com/[您的用户名]/academic-tracker.git .
# 如果是私有仓库，可能需要输入 GitHub 凭据或使用 Personal Access Token
```

### 2. 复制 .env 文件

```bash
# 如果您在根目录创建了 .env，直接使用
# 或者从 .env.example 复制并编辑
cp .env.example .env
nano .env  # 修改 SECRET_KEY 等配置
```

### 3. 使用 Docker Compose 启动

```bash
# 构建并启动容器
docker compose up -d --build

# 查看日志
docker compose logs -f

# 检查容器状态
docker compose ps
```

如果一切正常，您应该可以通过服务器 IP 访问网站了（假设防火墙已开放 80 端口）。

---

## 第五步：触发自动部署

完成上述步骤后，每次您推送代码到 GitHub 的 main 分支，GitHub Actions 会自动：

1. 构建 Docker 镜像
2. 通过 SSH 连接到服务器
3. 拉取最新代码
4. 重新构建并启动容器

### 测试部署

```bash
# 随便修改一个文件（比如 README.md）
# 提交并推送
git add .
git commit -m "Test deployment"
git push
```

然后在 GitHub 仓库的 **Actions** 页面查看部署进度。

---

## 常用管理命令

### 在服务器上

```bash
# 查看容器状态
cd /root/academic-tracker
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 启动服务
docker compose up -d

# 重新构建并启动
docker compose up -d --build

# 备份数据库（SQLite 文件）
cp /root/academic-tracker/data/data.db /root/academic-tracker/data/data.db.backup.$(date +%Y%m%d)
```

---

## 故障排查

### 如果 GitHub Actions 部署失败

1. 检查 Secrets 是否正确配置
2. 查看 Actions 日志中的错误信息
3. 尝试手动 SSH 登录到服务器测试连接

### 如果容器无法启动

```bash
# 查看详细日志
docker compose logs app

# 检查端口是否被占用
netstat -tlnp | grep :80
```

### 数据库问题

- SQLite 数据库文件存储在 `/root/academic-tracker/data/data.db`
- 这个目录通过 Docker volume 持久化，不会在容器重启时丢失

---

## 安全建议

1. **使用强密码**：特别是 SECRET_KEY 和 ADMIN_PASSWORD
2. **配置防火墙**：只开放必要的端口（80, 443, 22）
3. **定期更新**：保持 Docker 和依赖包最新
4. **定期备份**：备份数据库和重要文件
5. **使用 HTTPS**：建议配置 Nginx + Let's Encrypt 证书（可选进阶）
