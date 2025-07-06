# Celery启动脚本使用指南

## 脚本说明

### 1. start_celery_simple.sh (推荐用于开发和测试)
**用途**: 前台启动Celery Worker，适合开发调试  
**特点**: 
- 前台运行，可以看到详细日志
- 自动检查Redis连接
- macOS兼容模式 (使用线程池)
- 按Ctrl+C即可停止

**使用方法**:
```bash
cd backend
bash scripts/start_celery_simple.sh
```

### 2. start_celery.sh (完整的生产级脚本)
**用途**: 后台启动完整的Celery服务  
**特点**:
- 后台运行 (detach模式)
- 包含Worker、Beat调度器、Flower监控
- 支持启动/停止/重启/状态查看
- 自动生成PID文件和日志文件

**使用方法**:
```bash
cd backend

# 启动所有服务
bash scripts/start_celery.sh start

# 查看状态
bash scripts/start_celery.sh status

# 仅启动Worker
bash scripts/start_celery.sh worker

# 停止所有服务
bash scripts/start_celery.sh stop

# 重启所有服务
bash scripts/start_celery.sh restart
```

## 前置条件

1. **Redis服务运行**:
   ```bash
   # macOS使用Homebrew
   brew services start redis
   
   # 或手动启动
   redis-server
   ```

2. **Python依赖安装**:
   ```bash
   pip install -r requirements.txt
   ```

## 监控任务说明

系统会自动执行以下监控任务：

- **monitor_all_devices**: 监控所有启用的设备 (每5分钟)
- **monitor_single_device**: 监控单个设备
- **cleanup_old_logs**: 清理旧日志 (每2小时)

## 队列说明

- **default**: 默认队列
- **monitoring**: 设备监控任务
- **batch**: 批量任务
- **maintenance**: 维护任务

## 日志文件位置

```
backend/logs/celery/
├── worker.log      # Worker日志
├── beat.log        # Beat调度日志
├── flower.log      # Flower监控日志
├── worker.pid      # Worker进程ID
├── beat.pid        # Beat进程ID
└── flower.pid      # Flower进程ID
```

## 监控界面

启动Flower后可访问: http://localhost:5555

## 故障排除

1. **Redis连接失败**:
   - 确保Redis服务正在运行
   - 检查Redis配置 (默认localhost:6379)

2. **模块导入错误**:
   - 确保在backend目录下执行
   - 检查PYTHONPATH设置

3. **macOS fork错误**:
   - 脚本已自动使用线程池模式 (--pool=threads)

4. **端口占用**:
   - Flower默认使用5555端口
   - 可在start_celery.sh中修改端口设置 