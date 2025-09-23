<template>
  <div class="notice-card-container">
    <!-- 标题栏 -->
    <div class="notice-header" :class="{ 'new-notice-animation': newNoticeAnimation }">
      <div class="header-left">
        <el-icon class="notice-icon"><Bell /></el-icon>
        <span class="notice-title">通知公告</span>
        <el-badge 
          v-if="unreadCount > 0" 
          :value="unreadCount" 
          :max="99"
          class="unread-badge"
        />
      </div>
      <div class="header-right">
        <el-button 
          link 
          size="small" 
          @click="showAllNotices"
        >
          查看全部
        </el-button>
      </div>
    </div>

    <!-- 通知时间线 -->
    <div v-loading="loading" class="notice-timeline">
      <!-- 有通知时显示时间线 -->
      <el-timeline v-if="notices.length > 0" class="timeline-container">
        <el-timeline-item
          v-for="notice in displayNotices"
          :key="notice.noticeId"
          :timestamp="formatDate(notice.createTime)"
          :type="getTimelineType(notice)"
          :color="getTimelineColor(notice)"
          :icon="getTimelineIcon(notice)"
          placement="top"
          class="timeline-item"
          :class="{ 'unread': !isRead(notice.noticeId) }"
        >
          <div class="timeline-content" @click="viewNoticeDetail(notice.noticeId)">
            <div class="timeline-header">
              <h4 class="timeline-title">{{ notice.noticeTitle }}</h4>
              <div class="timeline-tags">
                <el-tag 
                  :type="getNoticeTypeTag(notice.noticeType)" 
                  size="small"
                  class="notice-type-tag"
                >
                  {{ getNoticeTypeText(notice.noticeType) }}
                </el-tag>
                <el-badge 
                  v-if="!isRead(notice.noticeId)" 
                  value="新" 
                  type="danger"
                  class="unread-badge-small"
                />
              </div>
            </div>
            <div class="timeline-meta">
              <span class="timeline-author">发布者：{{ notice.createBy }}</span>
              <span class="timeline-time">{{ formatDateTime(notice.createTime) }}</span>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>

      <!-- 无通知时的空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <el-icon class="empty-icon"><DocumentRemove /></el-icon>
        <p class="empty-text">暂无通知公告</p>
      </div>
    </div>

    <!-- 操作按钮区域 -->
    <div v-if="notices.length > displayCount" class="notice-footer">
      <el-button 
        link 
        size="small" 
        @click="loadMore"
        :loading="loadingMore"
      >
        加载更多 ({{ notices.length - displayCount }}条)
      </el-button>
    </div>

    <!-- 全部通知对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="全部通知公告"
      width="70%"
      :before-close="handleDialogClose"
      :z-index="3000"
      append-to-body
      :key="dialogKey"
    >
      <div class="dialog-notice-list">
        <div class="dialog-actions">
          <el-button 
            size="small" 
            @click="markAllAsRead"
            :disabled="unreadCount === 0"
          >
            全部标记已读
          </el-button>
        </div>
        
        <div v-loading="dialogLoading" class="dialog-content">
          <div 
            v-for="notice in allNotices" 
            :key="notice.noticeId"
            class="dialog-notice-item"
            :class="{ 'unread': !isRead(notice.noticeId) }"
            @click="viewNoticeDetailFromDialog(notice.noticeId)"
          >
            <div class="dialog-notice-content">
              <div class="dialog-notice-header">
                <span class="dialog-notice-title">{{ notice.noticeTitle }}</span>
                <div class="dialog-notice-tags">
                  <el-tag 
                    :type="getNoticeTypeTag(notice.noticeType)" 
                    size="small"
                  >
                    {{ getNoticeTypeText(notice.noticeType) }}
                  </el-tag>
                  <span v-if="!isRead(notice.noticeId)" class="unread-label">未读</span>
                </div>
              </div>
              <div class="dialog-notice-meta">
                <span class="dialog-notice-date">{{ formatDate(notice.createTime) }}</span>
                <span class="dialog-notice-author">发布者：{{ notice.createBy }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分页 -->
        <el-pagination
          v-if="dialogTotal > dialogPageSize"
          v-model:current-page="dialogCurrentPage"
          v-model:page-size="dialogPageSize"
          :total="dialogTotal"
          layout="total, prev, pager, next"
          @current-change="handleDialogPageChange"
          class="dialog-pagination"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { Bell, DocumentRemove, Message } from '@element-plus/icons-vue'
import { listNotice } from '@/api/system/notice'
import { 
  getUnreadCount, 
  isNoticeRead, 
  markNoticeAsRead, 
  markNoticesAsRead 
} from '@/utils/noticeStorage'
import websocketService from '@/utils/websocket'

// 路由
const router = useRouter()

// 组件props
const props = defineProps({
  // 首页显示的通知数量
  displayCount: {
    type: Number,
    default: 5
  },
  // 自动刷新间隔（分钟）
  refreshInterval: {
    type: Number,
    default: 5
  }
})

// 响应式数据
const loading = ref(false)
const loadingMore = ref(false)
const notices = ref([])
const displayNotices = computed(() => notices.value.slice(0, props.displayCount))

// 对话框相关
const dialogVisible = ref(false)
const dialogLoading = ref(false)
const allNotices = ref([])
const dialogCurrentPage = ref(1)
const dialogPageSize = ref(10)
const dialogTotal = ref(0)
const dialogKey = ref(0) // 用于强制重新渲染对话框

// 计算属性
const unreadCount = computed(() => getUnreadCount(notices.value))

// 新通知动画状态
const newNoticeAnimation = ref(false)

// WebSocket事件处理函数
const handleNewNotice = (data) => {
  console.log('[NoticeCard] 收到新通知:', data)
  
  try {
    const notice = data.notice
    const action = data.action
    
    if (action === 'notice_published') {
      // 显示新通知提示
      ElNotification({
        title: '📢 新通知公告',
        message: `${notice.notice_title}`,
        type: 'info',
        duration: 6000,
        position: 'top-right',
        showClose: true
      })
      
      // 触发动画效果
      newNoticeAnimation.value = true
      setTimeout(() => {
        newNoticeAnimation.value = false
      }, 1000)
      
      // 自动刷新通知列表
      fetchNotices()
      
      // 如果弹窗打开，也刷新弹窗数据
      if (dialogVisible.value) {
        fetchAllNotices()
        // 强制重新渲染弹窗
        dialogKey.value++
      }
      
      // 播放提示音（如果浏览器支持）
      playNotificationSound()
      
    } else if (action === 'notice_updated') {
      // 静默刷新列表
      fetchNotices()
      if (dialogVisible.value) {
        fetchAllNotices()
        dialogKey.value++
      }
    }
    
  } catch (error) {
    console.error('[NoticeCard] 处理新通知失败:', error)
  }
}

// 播放通知提示音
const playNotificationSound = async () => {
  try {
    // 创建一个短促的提示音
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    
    // 如果AudioContext被暂停，尝试恢复（需要用户交互）
    if (audioContext.state === 'suspended') {
      console.log('[NoticeCard] AudioContext被暂停，需要用户交互后才能播放提示音')
      return
    }
    
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
    oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1)
    
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2)
    
    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.2)
  } catch (error) {
    console.log('[NoticeCard] 无法播放提示音:', error)
  }
}

// 设置WebSocket事件监听器
const setupWebSocketListeners = () => {
  websocketService.on('new_notice', handleNewNotice)
}

// 清理WebSocket事件监听器
const cleanupWebSocketListeners = () => {
  websocketService.off('new_notice', handleNewNotice)
}

// 生命周期和事件处理
onMounted(() => {
  fetchNotices()
  // 设置自动刷新
  if (props.refreshInterval > 0) {
    setInterval(fetchNotices, props.refreshInterval * 60 * 1000)
  }
  
  // 设置WebSocket监听器
  setupWebSocketListeners()
})

onUnmounted(() => {
  // 清理WebSocket监听器
  cleanupWebSocketListeners()
})

// 获取通知列表
async function fetchNotices() {
  loading.value = true
  try {
    const response = await listNotice({
      pageNum: 1,
      pageSize: 20,
      // 只获取正常状态的通知
      status: '0'
    })
    // 按未读状态和创建时间排序（未读在前，然后按时间排序）
    const sortedNotices = (response.rows || []).sort((a, b) => {
      const aIsRead = isNoticeRead(a.noticeId)
      const bIsRead = isNoticeRead(b.noticeId)
      
      // 如果一个已读一个未读，未读的排在前面
      if (aIsRead !== bIsRead) {
        return aIsRead ? 1 : -1
      }
      
      // 如果都是已读或都是未读，按时间降序排序
      return new Date(b.createTime) - new Date(a.createTime)
    })
    notices.value = sortedNotices
  } catch (error) {
    console.error('获取通知列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载更多通知
async function loadMore() {
  loadingMore.value = true
  try {
    const response = await listNotice({
      pageNum: 1,
      pageSize: props.displayCount + 10,
      status: '0'
    })
    // 按未读状态和创建时间排序（未读在前，然后按时间排序）
    const sortedNotices = (response.rows || []).sort((a, b) => {
      const aIsRead = isNoticeRead(a.noticeId)
      const bIsRead = isNoticeRead(b.noticeId)
      
      // 如果一个已读一个未读，未读的排在前面
      if (aIsRead !== bIsRead) {
        return aIsRead ? 1 : -1
      }
      
      // 如果都是已读或都是未读，按时间降序排序
      return new Date(b.createTime) - new Date(a.createTime)
    })
    notices.value = sortedNotices
  } catch (error) {
    console.error('加载更多通知失败:', error)
    ElMessage.error('加载更多通知失败')
  } finally {
    loadingMore.value = false
  }
}

// 查看通知详情
function viewNoticeDetail(noticeId) {
  markNoticeAsRead(noticeId)
  router.push({
    name: 'NoticeDetail',
    params: { id: noticeId }
  })
}

// 从对话框查看通知详情
function viewNoticeDetailFromDialog(noticeId) {
  markNoticeAsRead(noticeId)
  
  // 延迟关闭对话框，让用户看到状态更新
  setTimeout(() => {
    dialogVisible.value = false
    router.push({
      name: 'NoticeDetail',
      params: { id: noticeId }
    })
  }, 100)
}

// 显示全部通知对话框
async function showAllNotices() {
  dialogVisible.value = true
  await fetchAllNotices()
}

// 获取全部通知（分页）
async function fetchAllNotices() {
  dialogLoading.value = true
  try {
    const response = await listNotice({
      pageNum: dialogCurrentPage.value,
      pageSize: dialogPageSize.value,
      status: '0'
    })
    // 按未读状态和创建时间排序（未读在前，然后按时间排序）
    const sortedNotices = (response.rows || []).sort((a, b) => {
      const aIsRead = isNoticeRead(a.noticeId)
      const bIsRead = isNoticeRead(b.noticeId)
      
      // 如果一个已读一个未读，未读的排在前面
      if (aIsRead !== bIsRead) {
        return aIsRead ? 1 : -1
      }
      
      // 如果都是已读或都是未读，按时间降序排序
      return new Date(b.createTime) - new Date(a.createTime)
    })
    allNotices.value = sortedNotices
    dialogTotal.value = response.total || 0
  } catch (error) {
    console.error('获取全部通知失败:', error)
    ElMessage.error('获取全部通知失败')
  } finally {
    dialogLoading.value = false
  }
}

// 处理对话框分页变化
function handleDialogPageChange() {
  fetchAllNotices()
}

// 全部标记已读
function markAllAsRead() {
  // 标记弹窗中显示的所有通知为已读
  const noticeIds = allNotices.value.map(notice => notice.noticeId)
  markNoticesAsRead(noticeIds)
  
  // 强制重新渲染对话框以更新已读状态显示
  dialogKey.value++
  
  ElMessage.success('已全部标记为已读')
}

// 关闭对话框
function handleDialogClose() {
  dialogVisible.value = false
  // 刷新首页通知列表
  fetchNotices()
}

// 工具方法
function isRead(noticeId) {
  return isNoticeRead(noticeId)
}

function getNoticeTypeText(type) {
  return type === '1' ? '通知' : '公告'
}

function getNoticeTypeTag(type) {
  return type === '1' ? 'warning' : 'success'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  // 一天内显示相对时间
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    const minutes = Math.floor(diff / (60 * 1000))
    
    if (hours > 0) {
      return `${hours}小时前`
    } else if (minutes > 0) {
      return `${minutes}分钟前`
    } else {
      return '刚刚'
    }
  }
  
  // 超过一天显示具体日期
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化完整日期时间
function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Timeline相关方法
function getTimelineType(notice) {
  if (!isRead(notice.noticeId)) {
    return 'primary'  // 未读为主要色
  }
  return notice.noticeType === '1' ? 'warning' : 'success'
}

function getTimelineColor(notice) {
  if (!isRead(notice.noticeId)) {
    return '#409eff'  // 未读为蓝色
  }
  return notice.noticeType === '1' ? '#e6a23c' : '#67c23a'
}

function getTimelineIcon(notice) {
  return notice.noticeType === '1' ? 'Bell' : 'Message'
}

// 暴露方法给父组件
defineExpose({
  refreshNotices: fetchNotices,
  getUnreadCount: () => unreadCount.value
})
</script>

<style lang="scss" scoped>
.notice-card-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.notice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .notice-icon {
      font-size: 18px;
    }
    
    .notice-title {
      font-size: 16px;
      font-weight: 600;
    }
    
    .unread-badge {
      :deep(.el-badge__content) {
        background-color: #f56c6c;
        border-color: #f56c6c;
      }
    }
  }
  
  .header-right {
    .el-button {
      color: #fff;
      
      &:hover {
        color: #f0f9ff;
      }
    }
  }
}

.notice-timeline {
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px 0;
  
  /* 默认隐藏滚动条 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  
  &::-webkit-scrollbar {
    width: 0px;
    background: transparent;
  }
  
  /* 鼠标悬停时显示滚动条 */
  &:hover {
    scrollbar-width: thin; /* Firefox */
    -ms-overflow-style: scrollbar; /* IE and Edge */
    
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 3px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 3px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
  }
}

/* 右侧侧边栏通知公告样式 */
.notice-sidebar-card {
  .notice-timeline {
    max-height: calc(100vh - 120px);
    min-height: 700px;
    
    /* 默认隐藏滚动条 */
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE and Edge */
    
    &::-webkit-scrollbar {
      width: 0px;
      background: transparent;
    }
    
    /* 鼠标悬停时显示滚动条 */
    &:hover {
      scrollbar-width: thin; /* Firefox */
      -ms-overflow-style: scrollbar; /* IE and Edge */
      
      &::-webkit-scrollbar {
        width: 6px;
      }
      
      &::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
      }
      
      &::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
        
        &:hover {
          background: #a8a8a8;
        }
      }
    }
  }
  
  .timeline-container {
    .timeline-item {
      .timeline-content {
        .timeline-header {
          .timeline-title {
            font-size: 13px;
            -webkit-line-clamp: 2;
          }
        }
        
        .timeline-meta {
          font-size: 11px;
        }
      }
    }
  }
  
  .notice-footer {
    position: sticky;
    bottom: 0;
    background: #fff;
    border-top: 1px solid #f0f2f5;
  }
}

/* 适配统计卡片样式 */
.notice-stat-card {
  .notice-card-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .notice-header {
    padding: 8px 12px;
    flex-shrink: 0;
    
    .header-left {
      .notice-title {
        font-size: 13px;
      }
      
      .notice-icon {
        font-size: 14px;
      }
    }
    
    .header-right {
      .el-button {
        font-size: 11px;
        padding: 2px 6px;
      }
    }
  }
  
  .notice-timeline {
    flex: 1;
    max-height: none;
    padding: 0 12px 8px;
    overflow-y: auto;
  }
  
  .timeline-container {
    .timeline-item {
      margin-bottom: 8px;
      
      :deep(.el-timeline-item__timestamp) {
        font-size: 10px;
      }
      
      .timeline-content {
        padding: 6px 8px;
        
        .timeline-header {
          margin-bottom: 4px;
          
          .timeline-title {
            font-size: 13px;
            -webkit-line-clamp: 2;
          }
          
          .timeline-tags {
            .notice-type-tag {
              font-size: 10px;
              padding: 0 4px;
              height: 16px;
              line-height: 16px;
            }
            
            .unread-badge-small {
              :deep(.el-badge__content) {
                font-size: 9px;
                padding: 0 4px;
                height: 14px;
                line-height: 14px;
              }
            }
          }
        }
        
        .timeline-meta {
          font-size: 10px;
          
          .timeline-time {
            display: inline;
          }
        }
      }
    }
  }
  
  .empty-state {
    padding: 20px 12px;
    
    .empty-icon {
      font-size: 24px;
    }
    
    .empty-text {
      font-size: 11px;
    }
  }
  
  .notice-footer {
    padding: 6px 12px;
    
    .el-button {
      font-size: 10px;
    }
  }
}

.timeline-container {
  :deep(.el-timeline) {
    padding-left: 0;
  }
  
  .timeline-item {
    &.unread {
      :deep(.el-timeline-item__node) {
        animation: pulse 2s infinite;
      }
    }
    
    .timeline-content {
      cursor: pointer;
      padding: 12px 16px;
      border-radius: 8px;
      border: 1px solid transparent;
      transition: all 0.3s ease;
      background-color: #fff;
      
      &:hover {
        background-color: #f5f7fa;
        border-color: #e4e7ed;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .timeline-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
        
        .timeline-title {
          flex: 1;
          font-size: 15px;
          font-weight: 600;
          color: #303133;
          line-height: 1.4;
          margin: 0 12px 0 0;
          
          // 最多显示两行
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        .timeline-tags {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
          
          .unread-badge-small {
            :deep(.el-badge__content) {
              font-size: 10px;
              padding: 0 6px;
              height: 16px;
              line-height: 16px;
            }
          }
        }
      }
      
      .timeline-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #909399;
        
        .timeline-author {
          color: #606266;
        }
        
        .timeline-time {
          color: #c0c4cc;
          font-size: 11px;
        }
      }
    }
  }
}

/* 未读通知动画效果 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #909399;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
    opacity: 0.5;
  }
  
  .empty-text {
    font-size: 14px;
    margin: 0;
  }
}

.notice-footer {
  padding: 12px 20px;
  text-align: center;
  border-top: 1px solid #f0f2f5;
  background-color: #fafafa;
}

// 对话框样式
.dialog-notice-list {
  .dialog-actions {
    margin-bottom: 16px;
    text-align: right;
  }
  
  .dialog-content {
    max-height: 500px;
    overflow-y: auto;
    
    /* 默认隐藏滚动条 */
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE and Edge */
    
    &::-webkit-scrollbar {
      width: 0px;
      background: transparent;
    }
    
    /* 鼠标悬停时显示滚动条 */
    &:hover {
      scrollbar-width: thin; /* Firefox */
      -ms-overflow-style: scrollbar; /* IE and Edge */
      
      &::-webkit-scrollbar {
        width: 6px;
      }
      
      &::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
      }
      
      &::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
        
        &:hover {
          background: #a8a8a8;
        }
      }
    }
  }
  
  .dialog-notice-item {
    padding: 16px;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    margin-bottom: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      border-color: #c6e2ff;
      background-color: #ecf5ff;
    }
    
    &.unread {
      border-color: #b3d8ff;
      background-color: #ecf5ff;
    }
    
    .dialog-notice-content {
      .dialog-notice-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
        
        .dialog-notice-title {
          flex: 1;
          font-size: 15px;
          font-weight: 500;
          color: #303133;
          line-height: 1.4;
          margin-right: 12px;
        }
        
        .dialog-notice-tags {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
          
          .unread-label {
            font-size: 12px;
            color: #f56c6c;
            font-weight: 500;
          }
        }
      }
      
      .dialog-notice-meta {
        display: flex;
        gap: 16px;
        font-size: 13px;
        color: #909399;
        
        .dialog-notice-date {
          color: #606266;
        }
      }
    }
  }
  
  .dialog-pagination {
    margin-top: 20px;
    text-align: center;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .notice-header {
    padding: 12px 16px;
    
    .header-left {
      .notice-title {
        font-size: 14px;
      }
    }
  }
  
  .notice-timeline {
    padding: 0 12px;
  }
  
  .timeline-container {
    .timeline-item {
      .timeline-content {
        padding: 10px 12px;
        
        .timeline-header {
          flex-direction: column;
          align-items: flex-start;
          gap: 8px;
          
          .timeline-title {
            margin-right: 0;
            font-size: 14px;
          }
          
          .timeline-tags {
            align-self: flex-end;
          }
        }
        
        .timeline-meta {
          flex-direction: column;
          align-items: flex-start;
          gap: 4px;
        }
      }
    }
  }
  
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
    z-index: 3000 !important;
  }
  
  :deep(.el-overlay) {
    z-index: 2999 !important;
  }
}

/* 新通知动画效果 */
.new-notice-animation {
  animation: newNoticeGlow 1s ease-in-out;
}

@keyframes newNoticeGlow {
  0% {
    box-shadow: 0 0 5px rgba(64, 158, 255, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(64, 158, 255, 0.8), 0 0 30px rgba(64, 158, 255, 0.6);
    transform: scale(1.02);
  }
  100% {
    box-shadow: 0 0 5px rgba(64, 158, 255, 0.5);
    transform: scale(1);
  }
}

/* 全局样式：确保通知对话框在最顶层 */
:global(.el-dialog__wrapper) {
  z-index: 3000 !important;
}

:global(.el-overlay-dialog) {
  z-index: 2999 !important;
}
</style>
