# 修复首页WebSocket连接状态显示问题

## 问题描述
当从首页切换至其他页面，再切换回首页时，实时连接显示为断开状态，但实际WebSocket连接可能仍然正常。

## 问题分析
1. WebSocket服务是全局单例，在应用启动时自动连接
2. 首页组件在挂载时设置事件监听器，卸载时清理监听器
3. 当组件重新挂载时，只设置了事件监听器，但没有检查当前连接状态
4. wsConnected状态只能通过WebSocket事件更新，组件切换时可能错过状态同步

## 解决方案
在首页组件的onMounted生命周期钩子中：
1. 设置WebSocket事件监听器
2. 主动检查当前WebSocket连接状态
3. 更新wsConnected响应式变量
4. 如果未连接则尝试重新连接

## 修改文件
- `frontend/src/views/redfish/dashboard/index.vue`

## 修改内容
在onMounted钩子中添加：
```javascript
// 主动检查WebSocket连接状态
wsConnected.value = websocketService.isConnected()

// 如果未连接，尝试重新连接
if (!wsConnected.value) {
  console.log('[Dashboard] WebSocket未连接，尝试重新连接...')
  websocketService.connect()
} else {
  console.log('[Dashboard] WebSocket已连接')
}
```

## 预期效果
用户在页面间切换后回到首页时，WebSocket连接状态能正确显示，不会出现"实时连接断开"的误报。

## 测试验证
1. 启动前端应用
2. 确认首页WebSocket连接状态显示正常
3. 切换到其他页面（如设备管理）
4. 切换回首页
5. 验证WebSocket连接状态是否正确显示

## 完成时间
2024年12月19日 