# Redfish 告警系统 API 测试指南

## 🚀 快速开始

### 1. 访问 Swagger UI
打开浏览器访问：`http://localhost:9099/dev-api/docs`

### 2. 认证流程

#### 步骤 1：获取验证码
1. 找到 **验证码模块** → `GET /captchaImage`
2. 点击 "Try it out" → "Execute"
3. 记录返回的 `uuid` 和 `img` 中的验证码

#### 步骤 2：用户登录
1. 找到 **登录模块** → `POST /login`
2. 点击 "Try it out"
3. 填写登录信息：
```json
{
  "username": "admin",
  "password": "admin123",
  "code": "验证码",
  "uuid": "步骤1获取的uuid"
}
```
4. 点击 "Execute"
5. 复制返回的 `access_token`

#### 步骤 3：设置认证
1. 点击页面右上角的 **🔒 Authorize** 按钮
2. 在 BearerAuth 输入框中粘贴 token（无需添加 "Bearer " 前缀）
3. 点击 "Authorize" → "Close"

## 📊 核心模块测试

### Redfish-设备管理 (9个接口)

#### 设备列表查询
- **接口**: `GET /redfish/devices`
- **参数**: 
  ```json
  {
    "pageNum": 1,
    "pageSize": 10,
    "device_name": "",
    "hostname": "",
    "business_ip": "",
    "location": "",
    "manufacturer": "",
    "health_status": ""
  }
  ```

#### 添加设备
- **接口**: `POST /redfish/devices`
- **示例数据**:
  ```json
  {
    "device_name": "服务器-002",
    "hostname": "web-server-02",
    "business_ip": "192.168.1.200",
    "oob_ip": "192.168.100.201",
    "oob_port": 443,
    "location": "XW_B1B03_20-24",
    "operating_system": "CentOS 7.9",
    "manufacturer": "hp",
    "serial_number": "test",
    "model": "PowerEdge R740",
    "technical_system": "Web服务系统",
    "system_owner": "张三",
    "business_purpose": "Web服务器",
    "business_type": "WEB",
    "redfish_username": "admin",
    "redfish_password": "password123",
    "monitor_enabled": 1,
    "remark": "生产环境Web服务器",
    "create_by": "",
    "create_time": "2025-06-08T10:15:07.895Z"
  }
  
  {
    "device_name": "string",
    "hostname": "string",
    "business_ip": "string",
    "oob_ip": "string",
    "oob_port": 443,
    "location": "string",
    "operating_system": "string",
    "serial_number": "string",
    "model": "string",
    "manufacturer": "string",
    "technical_system": "string",
    "system_owner": "string",
    "business_purpose": "string",
    "business_type": "string",
    "redfish_username": "string",
    "redfish_password": "string",
    "monitor_enabled": 1,
    "remark": "string",
    "create_by": "",
    "create_time": "2025-06-08T10:15:07.895Z"
  }
  ```

#### 设备连接测试
- **接口**: `POST /redfish/devices/{device_id}/test-connection`
- **说明**: 测试设备 Redfish 连接状态

### Redfish-告警管理 (12个接口)

#### 告警列表
- **接口**: `GET /redfish/alerts`
- **参数**:
  ```json
  {
    "pageNum": 1,
    "pageSize": 10,
    "alertLevel": "",
    "status": "",
    "deviceId": ""
  }
  ```

#### 告警统计
- **接口**: `GET /redfish/alerts/statistics`
- **返回**: 紧急/择期告警数量统计

#### 告警趋势
- **接口**: `GET /redfish/alerts/trend`
- **参数**: `days=7` (7天或30天)

### Redfish-首页数据 (8个接口)

#### 仪表盘概览
- **接口**: `GET /redfish/dashboard/overview`
- **返回**: 设备总数、告警统计、健康状态

#### 实时告警列表
- **接口**: `GET /redfish/dashboard/realtime-alerts`
- **说明**: 获取实时告警信息

#### 设备健康图表
- **接口**: `GET /redfish/dashboard/device-health-chart`
- **返回**: 设备健康状态分布数据

### Redfish-值班管理 (14个接口)

#### 值班人员管理
- **添加人员**: `POST /redfish/duty/persons`
  ```json
  {
    "name": "张三",
    "department": "运维部",
    "position": "高级工程师",
    "phone": "13800138000",
    "email": "zhangsan@company.com"
  }
  ```

#### 值班排期
- **添加排期**: `POST /redfish/duty/schedules`
  ```json
  {
    "personId": 1,
    "dutyDate": "2025-06-10",
    "dutyType": "day",
    "startTime": "09:00",
    "endTime": "18:00"
  }
  ```

#### 日历视图
- **接口**: `GET /redfish/duty/calendar`
- **参数**: `year=2025&month=6`

## 🔧 测试技巧

### 1. 批量测试
建议按以下顺序测试：
1. 设备管理 → 添加设备
2. 告警管理 → 查看告警
3. 首页数据 → 验证统计
4. 值班管理 → 人员和排期

### 2. 数据准备
- 先添加几个测试设备
- 创建一些测试告警数据
- 添加值班人员和排期

### 3. 错误处理测试
- 测试无效参数
- 测试权限验证
- 测试数据约束

## 📝 常见问题

### Q: Token 过期怎么办？
A: 重新执行登录流程获取新 token

### Q: 接口返回 401 错误？
A: 检查是否正确设置了 Bearer Token

### Q: 如何测试分页？
A: 修改 `pageNum` 和 `pageSize` 参数

### Q: 数据库为空怎么办？
A: 先使用 POST 接口添加测试数据

## 🎯 测试检查清单

- [ ] 成功登录并获取 token
- [ ] 设置 Bearer Token 认证
- [ ] 测试设备 CRUD 操作
- [ ] 验证告警管理功能
- [ ] 检查首页数据接口
- [ ] 测试值班管理功能
- [ ] 验证分页和搜索
- [ ] 测试错误处理

## 📊 API 接口总览

| 模块 | 接口数量 | 主要功能 |
|------|----------|----------|
| 设备管理 | 9 | 设备CRUD、连接测试、统计 |
| 告警管理 | 12 | 告警查询、统计、趋势分析 |
| 首页数据 | 8 | 仪表盘、图表、实时数据 |
| 值班管理 | 14 | 人员管理、排期、日历 |
| **总计** | **43** | **完整的告警系统功能** |

---

🎉 **恭喜！您现在可以开始全面测试 Redfish 告警系统的所有功能了！** 