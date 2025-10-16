#!/bin/bash
# =====================================================
# Celery 启动脚本（静默日志版）
# Author: Zheng Lilin
# 用法: bash scripts/start_celery.sh {start|stop|restart|status|worker|beat|flower}
# =====================================================

set -Eeuo pipefail
cd "$(dirname "$0")/.."

# --- 可选: 自动加载 .env.prod ---
# if [ -f backend/.env.prod ]; then
#   set -a; . backend/.env.prod; set +a
# fi

# --- Python 路径 ---
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# --- 配置参数，可被外部覆盖 ---
MODULE_PATH="${MODULE_PATH:-module_redfish.celery_config}"  # Celery 应用模块
CONCURRENCY="${CONCURRENCY:-4}"      # 并发数
POOL="${POOL:-threads}"              # 线程池类型：threads 或 prefork
QUEUES="${QUEUES:-default,monitoring,batch,maintenance}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_DB_BROKER="${REDIS_DB_BROKER:-1}"
REDIS_DB_BACKEND="${REDIS_DB_BACKEND:-2}"
FLOWER_PORT="${FLOWER_PORT:-5555}"

# --- 日志与PID目录 ---
LOG_DIR="logs/celery"
mkdir -p "$LOG_DIR"
PID_WORKER="$LOG_DIR/worker.pid"
PID_BEAT="$LOG_DIR/beat.pid"
PID_FLOWER="$LOG_DIR/flower.pid"
SCHED_FILE="$LOG_DIR/celerybeat-schedule"

# --- 工具函数 ---
is_running() { [[ -f "$1" ]] && kill -0 "$(cat "$1")" 2>/dev/null; }
kill_safely() {
  local pidfile="$1"
  if [[ -f "$pidfile" ]]; then
    local pid; pid="$(cat "$pidfile")" || true
    if kill -0 "$pid" 2>/dev/null; then
      kill -TERM "$pid" || true
      for i in {1..20}; do kill -0 "$pid" 2>/dev/null || break; sleep 0.3; done
      kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" || true
    fi
    rm -f "$pidfile"
  fi
}

# --- 启动 Worker ---
start_worker() {
  echo "🚀 启动 Celery Worker ..."
  local NODE_NAME="worker_$(hostname)_$(date +%s)"
  python3 -m celery -A "$MODULE_PATH" worker \
    --loglevel=warning \
    --concurrency="$CONCURRENCY" \
    --pool="$POOL" \
    --queues="$QUEUES" \
    --hostname="$NODE_NAME" \
    --logfile="$LOG_DIR/worker.log" \
    --pidfile="$PID_WORKER" \
    --detach
  echo "✅ Worker 已启动 (节点: $NODE_NAME, 日志: $LOG_DIR/worker.log)"
}

# --- 启动 Beat ---
start_beat() {
  echo "⏰ 启动 Celery Beat 调度器 ..."
  python3 -m celery -A "$MODULE_PATH" beat \
    --loglevel=warning \
    --logfile="$LOG_DIR/beat.log" \
    --pidfile="$PID_BEAT" \
    --schedule="$SCHED_FILE" \
    --detach
  echo "✅ Beat 已启动 (日志: $LOG_DIR/beat.log)"
}

# --- 启动 Flower ---
start_flower() {
  echo "🌼 启动 Flower 监控界面 ..."
  python3 -m celery -A "$MODULE_PATH" \
    --broker="redis://${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB_BROKER}" \
    flower \
    --port="$FLOWER_PORT" \
    --inspect_timeout=10 \
    --loglevel=warning \
    --logfile="$LOG_DIR/flower.log" \
    --pidfile="$PID_FLOWER" \
    --detach
  echo "✅ Flower 启动成功: http://localhost:${FLOWER_PORT}"
}

# --- 停止所有 ---
stop_all() {
  echo "🛑 停止 Celery 相关进程 ..."
  kill_safely "$PID_WORKER"
  kill_safely "$PID_BEAT"
  kill_safely "$PID_FLOWER"
  pkill -f "celery.*-A ${MODULE_PATH}" 2>/dev/null || true
  rm -f "$SCHED_FILE"
  echo "✅ 所有 Celery 进程已停止"
}

# --- 查看状态 ---
status() {
  echo "📋 Celery 状态："
  if is_running "$PID_WORKER"; then
    echo "✓ Worker 运行中 (PID: $(cat "$PID_WORKER"))"
  else
    echo "✗ Worker 未运行"
  fi
  if is_running "$PID_BEAT"; then
    echo "✓ Beat 运行中 (PID: $(cat "$PID_BEAT"))"
  else
    echo "✗ Beat 未运行"
  fi
  if is_running "$PID_FLOWER"; then
    echo "✓ Flower 运行中 (PID: $(cat "$PID_FLOWER"))"
  else
    echo "✗ Flower 未运行"
  fi
}

# --- 组合操作 ---
start_all() { start_worker; sleep 1; start_beat; sleep 1; start_flower; }
restart()   { stop_all; sleep 2; start_all; }

# --- 主入口 ---
case "${1:-}" in
  start)   start_all ;;
  stop)    stop_all ;;
  restart) restart ;;
  status)  status ;;
  worker)  start_worker ;;
  beat)    start_beat ;;
  flower)  start_flower ;;
  *)
    echo "使用方法: bash $0 {start|stop|restart|status|worker|beat|flower}"
    echo "示例: bash scripts/start_celery.sh start"
    ;;
esac

exit 0