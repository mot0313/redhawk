# 🔄 将 maintenance 权限统一为 businessRule 权限

## 📋 **统一方案说明**

您的想法非常合理！因为：

1. **排期规则页面** 实际上就是 **业务规则管理页面**
2. **功能一致性**: 页面内的所有功能都是通过 `business_rule_controller` 实现的
3. **权限语义清晰**: 避免 maintenance 和 businessRule 两套权限混淆
4. **后端无对应**: `maintenance_controller` 已经不存在了

## 🎯 **统一效果**

### 统一前
```
排期规则页面: redfish:maintenance:list
├── 紧急度规则: redfish:businessRule:*
├── 业务类型管理: redfish:businessRule:*
└── 硬件类型管理: redfish:businessRule:*
```

### 统一后
```
排期规则页面: redfish:businessRule:list
├── 紧急度规则: redfish:businessRule:*  
├── 业务类型管理: redfish:businessRule:*
└── 硬件类型管理: redfish:businessRule:*
```

## 📁 **需要修改的文件**

### 1. **数据库权限表**
- `sys_menu` 表中 menu_id=2400 的权限
- 删除其他未使用的 `redfish:maintenance:*` 权限

### 2. **权限设计脚本**
- `redesign_permission_system.sql` ✅ 已修改
- 其他清理脚本中的相关配置

## 🔧 **具体变更**

### 权限映射关系
| 原权限 | 新权限 | 说明 |
|--------|--------|------|
| `redfish:maintenance:list` | `redfish:businessRule:list` | 排期规则页面访问 |
| `redfish:maintenance:query` | `redfish:businessRule:query` | 业务规则查询 |
| `redfish:maintenance:add` | `redfish:businessRule:add` | 业务规则新增 |
| `redfish:maintenance:edit` | `redfish:businessRule:edit` | 业务规则修改 |
| `redfish:maintenance:remove` | `redfish:businessRule:remove` | 业务规则删除 |

### 菜单权限统一
```sql
-- 排期规则页面权限统一
UPDATE sys_menu 
SET perms = 'redfish:businessRule:list'
WHERE menu_id = 2400;

-- 删除冗余的maintenance权限
DELETE FROM sys_menu 
WHERE perms LIKE 'redfish:maintenance:%' 
  AND menu_id != 2400;
```

## ✅ **统一后的优势**

1. **语义统一**: 所有业务规则相关功能使用统一的权限前缀
2. **管理简化**: 不再需要维护两套相似的权限体系
3. **逻辑清晰**: 权限与实际功能实现完全对应
4. **避免混淆**: 消除 maintenance 和 businessRule 的歧义

## 🚀 **执行方案**

### 方案一：使用专用脚本（推荐）
```bash
psql -f unify_maintenance_to_businessrule.sql
```

### 方案二：手动SQL执行
```sql
-- 1. 更新排期规则页面权限
UPDATE sys_menu SET perms = 'redfish:businessRule:list' WHERE menu_id = 2400;

-- 2. 清理其他maintenance权限
DELETE FROM sys_role_menu WHERE menu_id IN (
    SELECT menu_id FROM sys_menu WHERE perms LIKE 'redfish:maintenance:%' AND menu_id != 2400
);
DELETE FROM sys_menu WHERE perms LIKE 'redfish:maintenance:%' AND menu_id != 2400;
```

## 📊 **影响评估**

### ✅ **正面影响**
- 权限体系更加清晰统一
- 管理维护成本降低  
- 避免权限配置混淆

### ⚠️ **注意事项**
- 需要重启应用清除权限缓存
- 普通用户权限需要重新分配
- 前端路由权限检查保持不变

**这个统一方案完全符合您系统的实际需求，建议立即执行！**
