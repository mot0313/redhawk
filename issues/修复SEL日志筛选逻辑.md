## 任务：修复SEL日志筛选逻辑

### 目标

严格按照 `check_redfish` 的标准，精确过滤 SEL 日志，只保留未修复的、需要关注的告警信息。

### 详细步骤

#### 1. 修改 `redfish_client.py`

- **文件**: `backend/module_redfish/redfish_client.py`
- **函数**: `get_log_service_entries`
- **逻辑**:
    1. 在处理每条日志的循环中，增加新的过滤逻辑。
    2. **跳过已修复**: 如果日志的 `Repaired` 字段为 `True`，则跳过。
    3. **跳过非问题**: 如果日志的 `Severity` 为 `OK` 或 `Informational`，则跳过。
    4. **分类告警**:
        - `Severity` 为 `Warning` -> `alert_level` = "择期"
        - `Severity` 为 `Critical`, `Error`等 -> `alert_level` = "紧急"

#### 2. 创建验证脚本

- **新文件**: `backend/test_sel_filter_logic.py`
- **目的**: 编写单元测试验证新逻辑。
- **方法**:
    1. 定义一组覆盖所有情况的**模拟日志数据**（已修复, OK, Warning, Critical）。
    2. 使用 `unittest.mock` **模拟 Redfish API 的响应**。
    3. 调用 `get_log_service_entries` 处理模拟数据。
    4. 使用 `assert` 语句检查返回结果是否与预期完全一致。 