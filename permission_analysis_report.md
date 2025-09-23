# 权限使用情况分析报告

## 📊 后端实际使用的权限 (CheckUserInterfaceAuth)

### 🔥 Redfish模块权限
#### Dashboard权限
- `redfish:dashboard:overview` ✅
- `redfish:dashboard:alert` ✅  
- `redfish:dashboard:device` ✅
- `redfish:dashboard:metrics` ✅
- `redfish:dashboard:view` ✅

#### 设备权限
- `redfish:device:list` ✅
- `redfish:device:query` ✅
- `redfish:device:add` ✅
- `redfish:device:edit` ✅
- `redfish:device:remove` ✅
- `redfish:device:test` ✅
- `redfish:device:import` ✅
- `redfish:device:export` ✅

#### 告警权限  
- `redfish:alert:list` ✅
- `redfish:alert:maintenance` ✅
- `redfish:alert:remove` ✅
- `redfish:alert:export` ✅

#### 日志权限
- `redfish:log:list` ✅
- `redfish:log:query` ✅
- `redfish:log:cleanup` ✅
- `redfish:log:remove` ✅
- `redfish:log:export` ✅
- `redfish:log:collect` ✅ (在收集接口中使用)
- `redfish:log:temp` ✅ (在临时日志接口中使用)
- `redfish:log:history` ✅ (在历史日志接口中使用)

#### 业务规则权限
- `redfish:businessRule:list` ✅
- `redfish:businessRule:query` ✅
- `redfish:businessRule:add` ✅
- `redfish:businessRule:edit` ✅
- `redfish:businessRule:remove` ✅

### 🔧 系统管理权限
#### 用户管理
- `system:user:list` ✅
- `system:user:query` ✅
- `system:user:add` ✅
- `system:user:edit` ✅
- `system:user:remove` ✅
- `system:user:export` ✅
- `system:user:import` ✅
- `system:user:resetPwd` ✅

#### 角色管理
- `system:role:list` ✅
- `system:role:query` ✅
- `system:role:add` ✅
- `system:role:edit` ✅
- `system:role:remove` ✅
- `system:role:export` ✅

#### 菜单管理
- `system:menu:list` ✅
- `system:menu:query` ✅
- `system:menu:add` ✅
- `system:menu:edit` ✅
- `system:menu:remove` ✅

#### 部门管理
- `system:dept:list` ✅
- `system:dept:query` ✅
- `system:dept:add` ✅
- `system:dept:edit` ✅
- `system:dept:remove` ✅

#### 岗位管理
- `system:post:list` ✅
- `system:post:query` ✅
- `system:post:add` ✅
- `system:post:edit` ✅
- `system:post:remove` ✅
- `system:post:export` ✅

#### 字典管理
- `system:dict:list` ✅
- `system:dict:query` ✅
- `system:dict:add` ✅
- `system:dict:edit` ✅
- `system:dict:remove` ✅
- `system:dict:export` ✅

#### 参数设置
- `system:config:list` ✅
- `system:config:query` ✅
- `system:config:add` ✅
- `system:config:edit` ✅
- `system:config:remove` ✅
- `system:config:export` ✅

#### 通知公告
- `system:notice:list` ✅
- `system:notice:query` ✅
- `system:notice:add` ✅
- `system:notice:edit` ✅
- `system:notice:remove` ✅

### 📈 系统监控权限
#### 在线用户
- `monitor:online:list` ✅
- `monitor:online:forceLogout` ✅

#### 定时任务
- `monitor:job:list` ✅
- `monitor:job:query` ✅
- `monitor:job:add` ✅
- `monitor:job:edit` ✅
- `monitor:job:remove` ✅
- `monitor:job:changeStatus` ✅
- `monitor:job:export` ✅

#### 操作日志
- `monitor:operlog:list` ✅
- `monitor:operlog:remove` ✅
- `monitor:operlog:export` ✅

#### 登录日志
- `monitor:logininfor:list` ✅
- `monitor:logininfor:remove` ✅
- `monitor:logininfor:export` ✅
- `monitor:logininfor:unlock` ✅

#### 服务监控
- `monitor:server:list` ✅

#### 缓存监控
- `monitor:cache:list` ✅

#### 监控配置
- `monitor:config:view` ✅
- `monitor:config:edit` ✅
- `monitor:task:view` ✅
- `monitor:task:execute` ✅
- `monitor:task:manage` ✅
- `monitor:system:view` ✅

### 🛠️ 系统工具权限
#### 代码生成
- `tool:gen:list` ✅
- `tool:gen:query` ✅
- `tool:gen:edit` ✅
- `tool:gen:remove` ✅
- `tool:gen:import` ✅
- `tool:gen:preview` ✅
- `tool:gen:code` ✅

---

## ❌ 数据库中有但后端未使用的权限

### Redfish模块
- `redfish:maintenance:query` ❌ (无对应controller)
- `redfish:maintenance:add` ❌ (无对应controller)
- `redfish:maintenance:edit` ❌ (无对应controller) 
- `redfish:maintenance:remove` ❌ (无对应controller)
- `redfish:log:temp:view` ❌ (具体未使用)
- `redfish:log:temp:collect` ❌ (具体未使用)
- `redfish:log:temp:export` ❌ (具体未使用)
- `redfish:log:history:view` ❌ (具体未使用)
- `redfish:alert:query` ❌ (告警查询功能整合在list中)

### 系统监控
- `monitor:druid:list` ❌ (druid监控已停用)
- `monitor:online:query` ❌ (整合在list中)
- `monitor:online:batchLogout` ❌ (批量强退功能未实现)
- `monitor:operlog:query` ❌ (整合在list中) 
- `monitor:logininfor:query` ❌ (整合在list中)

### 系统工具
- `tool:build:list` ❌ (表单构建功能已停用)
- `tool:swagger:list` ❌ (swagger接口权限未实际使用)

---

## ✅ 后端使用但数据库缺失的权限

目前分析显示，后端使用的权限在数据库中基本都有对应配置，没有发现明显缺失的权限。

---

## 📋 权限清理建议

### 立即删除的权限
1. `redfish:maintenance:*` (除list外) - 无对应后端实现
2. `redfish:log:temp:*` 详细权限 - 功能已整合
3. `redfish:log:history:view` - 功能已整合
4. `redfish:alert:query` - 功能已整合在list中
5. `monitor:druid:list` - 功能已停用
6. `monitor:*:query` 系列 - 功能已整合在list中
7. `monitor:online:batchLogout` - 功能未实现
8. `tool:build:list` - 功能已停用
9. `tool:swagger:list` - 权限未实际使用

### 保留但需要说明的权限
1. `redfish:maintenance:list` - 前端页面存在，用于业务规则管理
2. `redfish:log:collect` - 日志收集功能
3. `redfish:log:temp` - 临时日志功能
4. `redfish:log:history` - 历史日志功能

---

## 🎯 优化后的权限体系建议

### 核心原则
1. **一一对应**: 每个权限都应有对应的后端接口
2. **层级清晰**: 按模块和功能分组
3. **语义明确**: 权限名称能清楚表达功能
4. **最小权限**: 只保留实际需要的权限

### 推荐的权限分组
1. **redfish:dashboard:*** - 首页数据权限
2. **redfish:device:*** - 设备管理权限
3. **redfish:alert:*** - 告警管理权限
4. **redfish:log:*** - 日志管理权限
5. **redfish:businessRule:*** - 业务规则权限
6. **system:*** - 系统管理权限
7. **monitor:*** - 系统监控权限
8. **tool:gen:*** - 代码生成权限
