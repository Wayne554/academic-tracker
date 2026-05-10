#!/bin/bash
# Academic Tracker 部署脚本
# 使用方法：在服务器上运行 bash deploy.sh

echo "========================================="
echo "Academic Tracker - 部署脚本 v1.1.0"
echo "========================================="

# 1. 进入项目目录
cd ~/academic-tracker || {
  echo "❌ 错误：找不到 ~/academic-tracker 目录"
  echo "请先 clone 项目："
  echo "  cd ~"
  echo "  git clone https://github.com/Wayne554/academic-tracker.git"
  exit 1
}

# 2. 拉取最新代码
echo ""
echo "📦 正在拉取最新代码..."
git pull origin main

if [ $? -ne 0 ]; then
  echo "❌ Git pull 失败，请检查错误信息"
  exit 1
fi

# 3. 更新后端依赖
echo ""
echo "📚 正在更新后端依赖..."
cd backend
source venv/bin/activate || {
  echo "⚠️  虚拟环境不存在，正在创建..."
  python3 -m venv venv
  source venv/bin/activate
}
pip install -r requirements.txt

if [ $? -ne 0 ]; then
  echo "❌ 依赖安装失败"
  exit 1
fi

# 4. 重新构建前端
echo ""
echo "🏗️  正在重新构建前端..."
cd ~/academic-tracker/frontend
npm install
npm run build

if [ $? -ne 0 ]; then
  echo "❌ 前端构建失败"
  exit 1
fi

# 5. 重启服务提示
echo ""
echo "========================================="
echo "✅ 代码更新完成！"
echo "========================================="
echo ""
echo "请手动重启服务："
echo ""
echo "1️⃣  重启后端（终端1）："
echo "   cd ~/academic-tracker/backend"
echo "   source venv/bin/activate"
echo "   pkill -f 'uvicorn main:app'"
echo "   uvicorn main:app --host 0.0.0.0 --port 8000 --reload &"
echo ""
echo "2️⃣  重启 Caddy（终端2）："
echo "   pkill -9 caddy"
echo "   cd ~"
echo "   caddy run &"
echo ""
echo "或者如果您使用 systemd 服务，请运行："
echo "  sudo systemctl restart academic-tracker-backend"
echo "  sudo systemctl restart caddy"
echo ""
echo "========================================="
echo "部署完成！访问 http://119.28.14.122:8080 测试"
echo "========================================="
