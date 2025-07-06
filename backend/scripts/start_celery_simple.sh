#!/bin/bash

# 简单的Celery启动脚本
# 用于快速测试和开发

# 设置工作目录
cd "$(dirname "$0")/.."

echo "🚀 启动Celery Worker (前台运行，便于查看日志)..."
echo "📍 当前目录: $(pwd)"
echo "🔧 使用配置: module_redfish.celery_config"
echo "🍎 macOS兼容模式: 使用线程池"
echo ""

# 检查Redis连接
echo "🔍 检查Redis连接..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis连接正常"
else
    echo "❌ Redis连接失败，请确保Redis服务运行"
    echo "   提示: 可以使用 'brew services start redis' 启动Redis"
    exit 1
fi

echo ""
echo "🎯 启动Worker (按Ctrl+C停止)..."
echo "==========================================="
echo "📝 日志说明:"
echo "   - 看到 'celery@xxx ready.' 表示启动成功"
echo "   - 看到 'Task xxx received' 表示接收到任务"
echo "   - 看到 'Successfully connected to Redfish service' 表示设备连接成功"
echo ""

# 启动worker (前台运行，使用线程池避免macOS fork问题)
python3 -m celery -A module_redfish.celery_config worker --loglevel=info --concurrency=2 --pool=threads 