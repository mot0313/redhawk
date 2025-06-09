#!/bin/bash

# Celery启动脚本
# 用于启动Celery worker和beat调度器

# 设置工作目录
cd "$(dirname "$0")/.."

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Redis配置
export REDIS_HOST=${REDIS_HOST:-localhost}
export REDIS_PORT=${REDIS_PORT:-6379}
export REDIS_DB_BROKER=${REDIS_DB_BROKER:-1}
export REDIS_DB_BACKEND=${REDIS_DB_BACKEND:-2}

# 日志目录
LOG_DIR="logs/celery"
mkdir -p $LOG_DIR

# 函数：启动Celery Worker
start_worker() {
    echo "启动Celery Worker..."
    celery -A module_redfish.celery_tasks worker \
        --loglevel=info \
        --concurrency=4 \
        --queues=default,monitoring,batch,maintenance \
        --logfile=$LOG_DIR/worker.log \
        --pidfile=$LOG_DIR/worker.pid \
        --detach
    
    if [ $? -eq 0 ]; then
        echo "Celery Worker启动成功"
    else
        echo "Celery Worker启动失败"
        exit 1
    fi
}

# 函数：启动Celery Beat
start_beat() {
    echo "启动Celery Beat调度器..."
    celery -A module_redfish.celery_tasks beat \
        --loglevel=info \
        --logfile=$LOG_DIR/beat.log \
        --pidfile=$LOG_DIR/beat.pid \
        --detach
    
    if [ $? -eq 0 ]; then
        echo "Celery Beat启动成功"
    else
        echo "Celery Beat启动失败"
        exit 1
    fi
}

# 函数：启动Flower监控
start_flower() {
    echo "启动Flower监控界面..."
    celery -A module_redfish.celery_tasks flower \
        --port=5555 \
        --broker=redis://$REDIS_HOST:$REDIS_PORT/$REDIS_DB_BROKER \
        --logfile=$LOG_DIR/flower.log \
        --pidfile=$LOG_DIR/flower.pid \
        --detach
    
    if [ $? -eq 0 ]; then
        echo "Flower监控界面启动成功，访问地址: http://localhost:5555"
    else
        echo "Flower启动失败"
    fi
}

# 函数：停止所有Celery进程
stop_all() {
    echo "停止所有Celery进程..."
    
    # 停止worker
    if [ -f $LOG_DIR/worker.pid ]; then
        kill -TERM $(cat $LOG_DIR/worker.pid)
        rm -f $LOG_DIR/worker.pid
        echo "Celery Worker已停止"
    fi
    
    # 停止beat
    if [ -f $LOG_DIR/beat.pid ]; then
        kill -TERM $(cat $LOG_DIR/beat.pid)
        rm -f $LOG_DIR/beat.pid
        echo "Celery Beat已停止"
    fi
    
    # 停止flower
    if [ -f $LOG_DIR/flower.pid ]; then
        kill -TERM $(cat $LOG_DIR/flower.pid)
        rm -f $LOG_DIR/flower.pid
        echo "Flower已停止"
    fi
    
    # 清理beat调度文件
    rm -f celerybeat-schedule
}

# 函数：查看状态
status() {
    echo "检查Celery进程状态..."
    
    if [ -f $LOG_DIR/worker.pid ] && kill -0 $(cat $LOG_DIR/worker.pid) 2>/dev/null; then
        echo "✓ Celery Worker正在运行 (PID: $(cat $LOG_DIR/worker.pid))"
    else
        echo "✗ Celery Worker未运行"
    fi
    
    if [ -f $LOG_DIR/beat.pid ] && kill -0 $(cat $LOG_DIR/beat.pid) 2>/dev/null; then
        echo "✓ Celery Beat正在运行 (PID: $(cat $LOG_DIR/beat.pid))"
    else
        echo "✗ Celery Beat未运行"
    fi
    
    if [ -f $LOG_DIR/flower.pid ] && kill -0 $(cat $LOG_DIR/flower.pid) 2>/dev/null; then
        echo "✓ Flower正在运行 (PID: $(cat $LOG_DIR/flower.pid))"
    else
        echo "✗ Flower未运行"
    fi
}

# 函数：重启所有服务
restart() {
    echo "重启Celery服务..."
    stop_all
    sleep 3
    start_all
}

# 函数：启动所有服务
start_all() {
    start_worker
    sleep 2
    start_beat
    sleep 2
    start_flower
}

# 主程序
case "$1" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    worker)
        start_worker
        ;;
    beat)
        start_beat
        ;;
    flower)
        start_flower
        ;;
    *)
        echo "使用方法: $0 {start|stop|restart|status|worker|beat|flower}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动所有服务 (worker + beat + flower)"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  status  - 查看服务状态"
        echo "  worker  - 仅启动worker"
        echo "  beat    - 仅启动beat调度器"
        echo "  flower  - 仅启动flower监控"
        exit 1
        ;;
esac

exit 0 