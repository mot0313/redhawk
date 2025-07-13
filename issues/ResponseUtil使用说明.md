# ResponseUtil 使用说明

## 响应结构差异

### 使用 `data` 参数
```python
return ResponseUtil.success(data=result, msg='成功')
```

**响应结构**：
```json
{
  "code": 200,
  "msg": "成功",
  "success": true,
  "time": "2024-01-01T12:00:00",
  "data": {
    "totalDevices": 10,
    "onlineDevices": 8
  }
}
```

**前端访问**：
```javascript
const result = response.data
const count = result.totalDevices
```

### 使用 `model_content` 参数
```python
return ResponseUtil.success(model_content=response_model, msg='成功')
```

**响应结构**：
```json
{
  "code": 200,
  "msg": "成功", 
  "success": true,
  "time": "2024-01-01T12:00:00",
  "totalDevices": 10,
  "onlineDevices": 8
}
```

**前端访问**：
```javascript
const result = response  // 直接使用response，不是response.data
const count = result.totalDevices
```

## 关键差异

- **`data` 参数**：数据包装在 `data` 字段中
- **`model_content` 参数**：数据直接合并到响应根级别

## 最佳实践

1. **使用 `model_content`** 当你有完整的响应模型时
2. **使用 `data`** 当你有简单的数据对象时
3. **保持一致性** 在同一个API中使用相同的模式

## 连通性统计API示例

**后端**：
```python
response_model = ConnectivityStatsResponseModel.from_service_result(service_result)
return ResponseUtil.success(model_content=response_model, msg='获取连通性统计成功')
```

**前端**：
```javascript
getConnectivityStatistics().then(response => {
  // 注意：直接使用response，不是response.data
  const totalDevices = response.totalDevices
  const onlineDevices = response.onlineDevices
})
``` 