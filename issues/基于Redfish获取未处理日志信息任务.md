# 基于Redfish获取未处理日志信息任务

## 任务背景

用户需求：从Redfish获取日志信息，只需要获取未处理的日志信息，可以参考项目check_redfish的实现。

## 现有系统分析

### 已有功能：
1. **完整的日志管理系统**：
   - `RedfishAlertLog` 数据模型
   - `RedfishLogService` 服务层
   - `RedfishLogController` 控制器
   - 前端日志管理界面

2. **Redfish客户端**：
   - `RedfishClient` 类已实现设备状态获取
   - `DeviceMonitor` 实现状态分析和日志生成

### 缺少功能：
1. 直接的Redfish日志获取（SEL/MEL）
2. 未处理日志标识机制
3. 参考check_redfish的日志获取实现

## 实施计划

### 精简版方案（8-10小时）：
1. 扩展RedfishAlertLog模型，添加processed_status字段
2. 创建数据库迁移脚本
3. 扩展RedfishClient，参考check_redfish实现SEL/MEL日志获取
4. 扩展RedfishLogService，添加未处理日志方法
5. 扩展RedfishLogController，添加未处理日志API
6. 添加定时任务获取Redfish原始日志
7. 优化前端界面，添加未处理日志过滤

## 技术要点

### processed_status字段：
- `unprocessed`：新获取的未处理日志
- `processed`：已处理的日志  
- `ignored`：被忽略的日志

### Redfish日志端点：
- `/redfish/v1/Managers/{id}/LogServices/SEL/Entries`
- `/redfish/v1/Managers/{id}/LogServices/IML/Entries`

### 混合日志来源：
- 保留现有状态分析生成的日志（标记为processed）
- 新增直接从Redfish获取的原始日志（标记为unprocessed）

## 执行状态

- [x] 任务分析和计划制定
- [x] 数据模型扩展（添加processed_status、redfish_log_id、log_hash字段）
- [x] 数据库迁移（创建SQL脚本）
- [x] Redfish客户端扩展（参考check_redfish实现SEL/MEL日志获取）
- [x] 服务层扩展（添加未处理日志服务方法）
- [x] 控制器层扩展（添加未处理日志API接口）
- [x] 定时任务集成（每10分钟获取Redfish原始日志）
- [x] 前端界面优化（添加处理状态过滤和批量处理功能）

## 完成总结

✅ **功能实现完成**：
1. **数据模型扩展**：在RedfishAlertLog表中添加了processed_status、redfish_log_id、log_hash字段
2. **Redfish客户端增强**：新增get_event_logs、get_system_event_logs、get_management_event_logs方法
3. **服务层扩展**：添加get_unprocessed_logs_services、mark_logs_processed_services等方法
4. **API接口完善**：新增/redfish/log/unprocessed/list、/redfish/log/mark-processed等接口
5. **定时任务集成**：新增fetch_redfish_logs任务，每10分钟自动获取原始日志
6. **前端功能增强**：添加处理状态过滤、批量标记处理、选择功能

🔧 **技术特点**：
- **混合日志来源**：保留现有状态分析日志+新增Redfish原始日志
- **哈希去重机制**：避免重复日志存储
- **时间戳过滤**：高效的增量获取
- **批量处理**：支持批量标记已处理/忽略状态
- **向后兼容**：不影响现有日志管理功能

🔄 **架构修正**：
- **调度方式**：从Celery Beat改为现有APScheduler+数据库配置架构
- **任务管理**：通过sys_job表配置，支持前端界面管理
- **参数控制**：支持通过job_kwargs动态调整max_entries、log_type等参数
- **执行频率**：通过cron_expression配置，默认每10分钟执行

📋 **使用说明**：
1. 执行数据库迁移脚本：`backend/sql/add_unprocessed_log_fields.sql`
2. 执行定时任务配置脚本：`backend/sql/add_redfish_log_fetch_job.sql`
3. 重启后端服务使新功能生效
4. 前端日志页面现在支持按处理状态过滤和批量处理
5. 可通过"系统管理 > 定时任务"界面管理Redfish日志获取任务
6. 系统会自动每10分钟获取一次Redfish原始日志并标记为未处理 