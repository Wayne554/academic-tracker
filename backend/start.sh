#!/bin/bash
# 启动后端服务（支持并发）
# 使用多个 worker 以处理并发请求

cd "$(dirname "$0")"

# 确保依赖已安装
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# 启动 uvicorn，使用 4 个 worker
# --workers 4: 4 个进程并发处理请求
# --host 0.0.0.0: 允许外部访问
# --port 8000: 端口
# --reload: 开发时自动重载（生产环境请删除此参数）

echo "启动 Academic Tracker 后端..."
echo "访问地址: http://0.0.0.0:8000"
echo "API 文档: http://0.0.0.0:8000/docs"
echo ""
echo "提示: 按 Ctrl+C 停止服务"
echo "================================"
echo ""

uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000 --reload
