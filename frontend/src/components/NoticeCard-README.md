# NoticeCard 通知公告组件

## 功能特点

### 🎨 Timeline 时间线样式
- 使用 Element Plus Timeline 组件展示通知公告
- 美观的时间线布局，清晰显示发布时间
- 不同通知类型使用不同的图标和颜色
- 未读通知有动画效果和特殊标识

### 🔔 未读提示功能
- 头部徽章显示未读数量
- 未读通知有蓝色脉冲动画效果
- 单独的"新"徽章标识
- 点击自动标记为已读

### ⭐ 交互体验
- 悬停时卡片上浮效果
- 平滑的动画过渡
- 响应式设计，移动端适配
- 一键查看全部通知

## Timeline 样式说明

### 通知类型标识
- **通知（type='1'）**：Bell 图标，橙色
- **公告（type='2'）**：Message 图标，绿色
- **未读通知**：蓝色，带脉冲动画

### 时间显示
- **时间戳位置**：placement="top"
- **相对时间**：如"2小时前"、"刚刚"
- **详细时间**：鼠标悬停或元数据区域

### 动画效果
- **未读通知**：2秒循环的蓝色脉冲动画
- **悬停效果**：向上平移 + 阴影
- **标签动画**：流畅的颜色过渡

## 使用方法

```vue
<template>
  <NoticeCard 
    :display-count="5" 
    :refresh-interval="5" 
  />
</template>

<script setup>
import NoticeCard from '@/components/NoticeCard.vue'
</script>
```

## Props

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| displayCount | Number | 5 | 首页显示的通知数量 |
| refreshInterval | Number | 5 | 自动刷新间隔（分钟） |

## 样式定制

### 自定义颜色
```scss
// 未读通知动画颜色
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7); }
  70% { box-shadow: 0 0 0 8px rgba(64, 158, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0); }
}

// Timeline 节点颜色
.timeline-item.unread :deep(.el-timeline-item__node) {
  border-color: #409eff;
  background-color: #409eff;
}
```

### 自定义图标
可以在 `getTimelineIcon()` 方法中修改图标：

```javascript
function getTimelineIcon(notice) {
  // 自定义图标逻辑
  if (notice.noticeType === '1') {
    return 'Bell'      // 通知
  } else {
    return 'Message'   // 公告
  }
}
```
