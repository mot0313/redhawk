# Redfish监控系统测试指导 (原有APScheduler架构)

## 系统架构

```
FastAPI应用启动 → APScheduler初始化 → Redfish监控任务注册 → 每5分钟自动触发 → Celery异步执行 → 数据库存储 → WebSocket推送
```

**重要**: 项目已集成完整的APScheduler系统，**应用启动时会自动**：
1. 初始化APScheduler调度器 (`SchedulerUtil.init_system_scheduler()`)
2. 注册Redfish监控任务 (`RedfishSchedulerTasks.init_monitoring_tasks()`)
3. 开始定时监控 (每5分钟自动执行)

## 快速测试流程

### 方法1：完整应用测试 (推荐)

#### 1. 启动FastAPI应用
```bash
cd backend
python3 app.py
```
此时APScheduler和Redfish监控任务已自动启动！

#### 2. 启动Celery Worker (新终端)
```bash
cd backend  
bash scripts/start_celery_simple.sh
```

#### 3. 访问Web管理界面
```bash
# 定时任务管理
http://localhost:9099/monitor/job

# 前端Dashboard
http://localhost:3000
```

### 方法2：独立测试脚本

如果只想测试监控功能而不启动Web应用：

```bash
cd backend

# 运行基于现有架构的测试
python3 test_existing_scheduler.py
```

## 系统验证要点

### ✅ APScheduler验证
1. **应用启动日志**: 看到 "系统初始定时任务加载成功"
2. **任务注册**: 查看 `/monitor/job` 页面的定时任务列表
3. **自动执行**: 每5分钟自动触发监控
4. **手动触发**: 可通过Web界面手动执行

### ✅ Celery集成验证  
1. **任务提交**: APScheduler触发时，任务提交到Celery队列
2. **异步执行**: Celery Worker处理监控任务
3. **并发处理**: 支持1000台设备并发监控
4. **结果回传**: 监控结果存储到数据库

### ✅ 监控功能验证
1. **设备连接**: 成功连接Redfish接口
2. **硬件数据**: 获取CPU、内存、存储、电源、温度信息
3. **告警生成**: 异常状态自动生成告警
4. **实时推送**: WebSocket推送状态变化

## Web界面管理

### 定时任务管理 (`/monitor/job`)
- 查看所有定时任务
- 手动触发任务执行
- 修改任务状态 (启用/禁用)
- 查看任务执行日志
- 导出任务配置

### 设备管理
- 添加/编辑监控设备
- 启用/禁用设备监控
- 查看设备健康状态
- 设备告警查看

### Dashboard实时监控
- 设备状态实时更新
- 告警统计图表
- 趋势分析
- WebSocket实时推送

## 测试命令总结

```bash
# 1. 启动完整系统
cd backend
python3 app.py                          # 主应用 (包含APScheduler)
bash scripts/start_celery_simple.sh     # Celery Worker

# 2. 独立测试
python3 test_existing_scheduler.py      # 测试APScheduler集成

# 3. 传统Celery测试  
python3 test_monitoring_flow.py         # 测试Celery任务

# 4. 系统管理
redis-cli ping                          # 检查Redis
curl http://localhost:9099/monitor/job  # 检查定时任务API
```

## 配置修改

### 监控间隔调整
```python
# 通过代码修改
RedfishSchedulerTasks.update_monitor_interval(10)  # 改为10分钟

# 或通过Web界面修改定时任务的Cron表达式
```

### Celery并发调整
```bash
# 修改Worker并发数
python3 -m celery -A module_redfish.celery_config worker --concurrency=8 --pool=threads
```

## 故障排除

### ❌ APScheduler未启动
- 检查应用启动日志
- 确认 `init_system_scheduler()` 被调用
- 查看 `/monitor/job` 是否可访问

### ❌ 定时任务不执行
- 检查任务状态是否为"正常"  
- 查看任务执行日志
- 确认Cron表达式正确
- 验证Celery Worker运行

### ❌ Celery任务失败
- 查看Worker日志中的错误信息
- 检查设备连接和认证
- 验证数据库字段匹配
- 确认Redis连接正常

## 架构优势

1. **集成性**: APScheduler与FastAPI完全集成
2. **可管理性**: Web界面管理所有定时任务
3. **可扩展性**: 支持多种定时任务，不限于监控
4. **可监控性**: 完整的任务执行日志和状态跟踪
5. **高性能**: APScheduler + Celery 双重异步处理

## 下一步建议

1. **完善Web界面**: 优化前端Dashboard展示
2. **增强监控**: 添加更多硬件监控指标
3. **告警通知**: 集成邮件、短信等通知渠道
4. **性能优化**: 根据设备数量调整并发参数
5. **数据分析**: 添加历史数据分析和趋势预测 