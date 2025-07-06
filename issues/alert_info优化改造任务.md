# Alert_info表优化改造任务

## 任务背景
用户需求：优化首页告警展示，只显示设备的故障组件状态和紧急程度，详细的redfish日志信息在其他菜单中显示。

## 任务目标
1. 精简alert_info表结构，优化查询性能
2. 首页只显示核心状态信息：设备+组件+健康状态+紧急程度
3. 详细告警日志信息存储在redfish_alert_log表中
4. 保持现有硬件排期功能不受影响

## 实施方案

### 第一阶段：数据库结构改造 ✅ 已完成
- ✅ 设计精简版alert_info表结构（alert_info_optimized.sql）
- ✅ 创建数据迁移脚本（alert_info_migration.sql）
- ✅ 为每个字段添加详细注释
- ✅ 优化索引设计，提升查询性能

### 第二阶段：后端代码改造 ✅ 已完成
- ✅ 更新AlertInfo模型类，精简字段定义（models.py）
- ✅ 更新AlertVO模型，适配新字段结构（alert_vo.py）
- ✅ 创建优化版AlertDao，专注首页查询性能（alert_dao_optimized.py）
- [ ] 调整AlertService业务逻辑，使用新DAO
- [ ] 更新AlertController接口，返回精简数据
- [ ] 确保MaintenanceService排期功能兼容性

### 第三阶段：前端界面改造（待执行）
- [ ] 优化首页告警列表显示
- [ ] 新增设备日志管理页面
- [ ] 调整告警详情页面
- [ ] 更新API接口调用

### 第四阶段：测试验证（待执行）
- [ ] 数据库迁移测试
- [ ] 功能完整性测试
- [ ] 性能优化验证
- [ ] 用户体验测试

## 核心设计要点

### 精简字段列表
| 字段名 | 类型 | 说明 | 首页展示 |
|--------|------|------|----------|
| alert_id | bigserial | 告警ID（主键） | - |
| device_id | bigint | 设备ID | ✅ 显示设备名称 |
| component_type | varchar(50) | 组件类型 | ✅ 核心显示 |
| component_name | varchar(100) | 组件名称 | ✅ 具体组件 |
| health_status | varchar(20) | 健康状态 | ✅ 状态显示 |
| urgency_level | varchar(20) | 紧急程度 | ✅ 分类显示 |
| alert_status | varchar(20) | 告警状态 | - |
| first_occurrence | timestamp | 首次发生时间 | ✅ 时间排序 |
| last_occurrence | timestamp | 最后发生时间 | - |
| resolved_time | timestamp | 解决时间 | - |

### 性能优化索引
- device_id + component_type：设备组件查询
- urgency_level + alert_status：分类查询
- health_status：状态筛选
- first_occurrence：时间排序

### 数据分离策略
- **alert_info表**：存储组件状态汇总，用于首页快速展示
- **redfish_alert_log表**：存储详细日志信息，用于故障排查

## 风险控制
1. 数据备份：迁移前自动创建alert_info_backup表
2. 兼容性：确保硬件排期功能正常运行
3. 回滚方案：保留原表结构备份
4. 分步执行：数据库改造与代码改造分开进行

## 执行计划
- 当前状态：第一阶段已完成，等待用户确认执行第二阶段
- 下一步：更新后端模型和业务逻辑代码
- 预计完成时间：2-3个工作日

## 相关文件
- `backend/sql/alert_info_optimized.sql` - 优化后的表结构
- `backend/sql/alert_info_migration.sql` - 数据迁移脚本
- 待更新：AlertInfo模型、AlertDao、AlertService、AlertController 