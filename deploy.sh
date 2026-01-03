#!/bin/bash

# ====================================
# 职场情绪充电站 - 部署脚本
# ====================================

set -e

echo "===================================="
echo "  职场情绪充电站 - 部署脚本"
echo "===================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印成功消息
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 函数：打印警告消息
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 函数：打印错误消息
error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查环境变量配置文件
if [ ! -f .env.production ]; then
    error "未找到 .env.production 文件"
    warning "请先配置 .env.production 文件中的 API_BASE_URL"
    warning "示例：API_BASE_URL=https://your-domain.com"
    exit 1
fi

# 检查是否设置了域名
DOMAIN=$(grep "^API_BASE_URL=" .env.production | cut -d'=' -f2)
if [ "$DOMAIN" == "https://your-domain.com" ] || [ -z "$DOMAIN" ]; then
    error "请在 .env.production 中设置正确的 API_BASE_URL"
    exit 1
fi

success "域名配置: $DOMAIN"

# 安装依赖
echo ""
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt -q
success "依赖安装完成"

# 检查 Python 环境
echo ""
echo "🐍 检查 Python 环境..."
python --version
success "Python 环境正常"

# 检查端口是否被占用
PORT=$(grep "^API_PORT=" .env.production | cut -d'=' -f2)
if [ -z "$PORT" ]; then
    PORT=5000
fi

echo ""
echo "🔍 检查端口 $PORT..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    warning "端口 $PORT 已被占用"
    read -p "是否尝试停止占用进程？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
        success "已停止占用进程"
    else
        error "请先停止占用端口的进程"
        exit 1
    fi
fi

# 加载环境变量
echo ""
echo "🔧 加载环境变量..."
export $(grep -v '^#' .env.production | xargs)
success "环境变量加载完成"

# 启动服务
echo ""
echo "🚀 启动 API 服务..."
echo "===================================="
echo "服务地址: $API_BASE_URL"
echo "监听端口: $API_PORT"
echo "===================================="
echo ""

# 使用 nohup 后台运行
nohup python backend_api.py > api.log 2>&1 &
PID=$!

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 检查服务是否运行
if ps -p $PID > /dev/null; then
    success "API 服务启动成功！"
    echo ""
    echo "===================================="
    echo "  部署信息"
    echo "===================================="
    echo "PID: $PID"
    echo "日志文件: api.log"
    echo "服务地址: $API_BASE_URL"
    echo "健康检查: $API_BASE_URL/api/health"
    echo "测试页面: $API_BASE_URL/index.html"
    echo "===================================="
    echo ""
    echo "查看日志: tail -f api.log"
    echo "停止服务: kill $PID"
else
    error "API 服务启动失败，请查看日志: api.log"
    exit 1
fi
