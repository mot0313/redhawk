# Redfish日志管理功能说明

## 功能概述

Redfish日志管理是一个轻量级的设备日志收集和管理系统，用于获取和管理不同设备的Redfish日志信息，与硬件告警信息区分开来。

### 核心特性

- **轻量级设计**：只存储Critical和Warning级别的日志
- **数据控制**：自动保留30天，过期自动清理
- **实时收集**：支持手动和自动收集设备日志
- **高效查询**：多维度筛选和分页查询
- **数据导出**：支持日志数据导出功能

## 功能对比

| 功能特性 | 日志管理 | 硬件告警 |
|---------|---------|---------|
| **数据来源** | Redfish Event Logs (SEL/MEL) | 设备组件状态检查 |
| **用途** | 历史事件记录、问题溯源 | 实时监控、即时响应 |
| **数据级别** | Critical/Warning | 所有级别 |
| **保存时间** | 30天自动清理 | 长期保存 |
| **更新频率** | 按需收集 | 定时监控(5分钟) |

## 系统架构

### 后端架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Controller     │    │    Service      │    │      DAO        │
│ (REST API)      │────│  (业务逻辑)      │────│   (数据访问)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面        │    │  Redfish Client │    │   数据库表       │
│  (Vue3组件)      │    │   (设备通信)     │    │ (redfish_log)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 数据库设计
```sql
-- 主要字段
log_id          UUID        -- 主键
device_id       INTEGER     -- 设备ID
device_ip       VARCHAR     -- 设备IP
log_source      VARCHAR     -- 日志来源(SEL/MEL)
severity        VARCHAR     -- 严重程度(CRITICAL/WARNING)
created_time    TIMESTAMP   -- 日志创建时间
message         TEXT        -- 日志消息
```

## 安装部署

### 1. 数据库初始化
```bash
cd backend
psql -h localhost -U postgres -d redhawk_manager -f sql/init_redfish_log_management.sql
```

### 2. 启用定时任务
1. 登录系统管理界面
2. 进入"系统管理" → "定时任务"
3. 找到"Redfish日志清理任务"
4. 点击"启用"按钮

### 3. 配置权限
确保用户角色具有以下权限：
- `redfish:log:list` - 查看日志列表
- `redfish:log:query` - 查看日志详情
- `redfish:log:collect` - 收集日志
- `redfish:log:export` - 导出日志
- `redfish:log:remove` - 删除日志
- `redfish:log:cleanup` - 清理日志

## 使用指南

### 菜单访问
- 路径：**设备管理** → **日志管理**
- 组件：`frontend/src/views/redfish/log/index.vue`

### 主要功能

#### 1. 日志查询
- **多维度筛选**：设备IP、日志来源、严重程度、时间范围
- **关键词搜索**：支持消息内容搜索
- **分页显示**：高效的分页查询

#### 2. 日志收集
- **设备选择**：可选择单个设备或全部设备
- **日志类型**：SEL(系统事件日志)、MEL(管理事件日志)、全部
- **增量收集**：避免重复收集，支持强制刷新

#### 3. 统计信息
- **总体统计**：总数量、严重/警告分布
- **时间统计**：今日日志、近7天日志
- **来源统计**：SEL/MEL日志分布

#### 4. 管理功能
- **删除日志**：支持单条或批量删除
- **清理日志**：手动清理指定天数前的日志
- **导出数据**：导出Excel格式的日志数据

## API接口

### 核心接口
```
GET    /redfish/log/list          # 获取日志列表
GET    /redfish/log/statistics    # 获取统计信息
GET    /redfish/log/{log_id}      # 获取日志详情
POST   /redfish/log/collect       # 收集设备日志
POST   /redfish/log/cleanup       # 清理旧日志
DELETE /redfish/log/{log_id}      # 删除单条日志
DELETE /redfish/log/device/{id}   # 删除设备所有日志
GET    /redfish/log/export/data   # 导出日志数据
```

### 请求示例
```bash
# 收集所有设备的日志
curl -X POST "http://localhost:8000/redfish/log/collect" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": null,
    "log_type": "all",
    "max_entries": 100,
    "force_refresh": false
  }'

# 查询日志列表
curl "http://localhost:8000/redfish/log/list?severity=CRITICAL&page_size=20"
```

## 定时任务

### 日志清理任务
- **任务名称**：Redfish日志清理任务
- **执行时间**：每天凌晨2:00
- **清理规则**：删除30天前的所有日志记录
- **配置路径**：系统管理 → 定时任务

### 手动执行
```bash
# 在系统管理-定时任务中手动触发任务
# 或在Python环境中直接调用：
cd backend
python -c "
from module_task.redfish_monitor_tasks import redfish_log_cleanup_job
result = redfish_log_cleanup_job()
print(result)
"
```

## 性能优化

### 数据库索引
```sql
-- 主要索引
idx_redfish_log_device_id      -- 设备ID
idx_redfish_log_severity       -- 严重程度
idx_redfish_log_created_time   -- 创建时间
idx_redfish_log_device_time    -- 设备+时间复合索引
```

### 数据量控制
- **存储策略**：只保存Critical/Warning级别
- **时间限制**：30天自动清理
- **预估容量**：1000台设备约30万条记录(300MB)

### 查询优化
- **分页查询**：避免大量数据加载
- **索引使用**：充分利用数据库索引
- **缓存策略**：统计信息适当缓存

## 故障排查

### 常见问题

1. **日志收集失败**
   - 检查设备连接状态
   - 验证Redfish认证信息
   - 查看错误日志

2. **定时任务不执行**
   - 确认任务状态为"正常"
   - 检查Cron表达式
   - 查看调度器日志

3. **查询性能慢**
   - 缩小时间范围
   - 使用设备筛选
   - 检查数据库索引

### 日志文件
- **应用日志**：`backend/logs/`
- **任务日志**：在定时任务执行记录中查看
- **数据库日志**：PostgreSQL日志

## 开发扩展

### 添加新的日志来源
1. 扩展`RedfishClient.get_event_logs()`方法
2. 更新`log_source`枚举值
3. 修改前端筛选选项

### 自定义清理策略
1. 修改`module_task.redfish_monitor_tasks.redfish_log_cleanup_job()`
2. 在sys_job表中调整定时任务参数
3. 更新RedfishLogService的清理逻辑

### 增强统计功能
1. 扩展`RedfishLogDao.get_redfish_log_stats()`
2. 添加新的统计维度
3. 更新前端展示组件

## 维护指南

### 日常维护
- 监控磁盘空间使用
- 检查定时任务执行状态
- 定期备份重要日志数据

### 升级注意事项
- 数据库结构变更时的迁移脚本
- 新版本功能的权限配置
- 兼容性测试和回滚方案
