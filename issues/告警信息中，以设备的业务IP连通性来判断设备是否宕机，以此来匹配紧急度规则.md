# 告警信息中，以设备的业务IP连通性来判断设备是否宕机，以此来匹配紧急度规则

## 需求描述
在现有的告警系统中，增加设备业务IP连通性检查，以判断设备是否宕机，并根据业务规则匹配相应的紧急度。

## 实现方案
采用方案A：新增"connectivity"组件类型，通过现有的business_hardware_urgency_rules表来配置紧急度。

## 代码修改

### 1. DeviceMonitor修改 (backend/module_redfish/device_monitor.py)
- 导入ConnectivityService
- 在_analyze_status方法开头添加业务IP连通性检查
- 生成connectivity组件状态：
  - component_type: "connectivity"
  - component_name: "宕机"  
  - health_status: "ok"(在线) 或 "critical"(离线)
- 离线时生成告警条目

### 2. 数据库配置
需要在hardware_type_dict和business_hardware_urgency_rules表中添加connectivity相关配置：

#### 2.1 硬件类型字典
```sql
-- 在hardware_type_dict表中添加connectivity类型
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES
('connectivity', '宕机', '设备业务IP连通性检查', '网络', 100, 1, 'system', NOW(), 'system', NOW());
```

#### 2.2 紧急度规则
```sql
-- 示例：为不同业务类型配置connectivity的紧急度
-- 注意：hardware_type使用小写'connectivity'以匹配component_type
INSERT INTO business_hardware_urgency_rules (business_type, hardware_type, urgency_level, description, is_active, create_by, create_time, update_by, update_time) VALUES
('生产系统', 'connectivity', 'urgent', '生产系统宕机为紧急', 1, 'system', NOW(), 'system', NOW()),
('测试系统', 'connectivity', 'scheduled', '测试系统宕机为择期', 1, 'system', NOW(), 'system', NOW()),
('开发系统', 'connectivity', 'scheduled', '开发系统宕机为择期', 1, 'system', NOW(), 'system', NOW());
```

**重要说明**：
- `component_type`在DeviceMonitor中设置为"connectivity"
- `hardware_type`在数据库规则中必须也是"connectivity"（小写）
- 两者必须完全匹配，因为save_monitoring_result使用`(business_type, component_type)`作为键查询规则

## 工作流程
1. DeviceMonitor监控设备时，首先检查business_ip连通性
2. 根据连通性结果生成connectivity组件状态
3. save_monitoring_result处理all_components时，发现critical状态会创建告警
4. 告警的urgency_level通过business_hardware_urgency_rules表匹配：
   - 查询条件：business_type + hardware_type='connectivity'
   - 未匹配到规则时默认为'scheduled'

## 优势
- 与现有告警流程完全兼容
- 通过数据库配置灵活调整不同业务的宕机紧急度
- 可在前端将connectivity作为普通组件展示
- 代码改动集中，易于维护

## 完成状态
- [x] 修改DeviceMonitor添加连通性检查
- [x] 确认health_status映射正确
- [ ] 提供数据库规则配置SQL
- [ ] 编写/更新测试用例 