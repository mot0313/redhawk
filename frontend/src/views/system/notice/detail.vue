<template>
  <div class="app-container">
    <!-- 面包屑导航 -->
    <el-breadcrumb class="breadcrumb-container" separator="/">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>通知详情</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 加载状态 -->
    <div v-loading="loading" class="notice-detail-container">
      
      <!-- 通知详情卡片 -->
      <el-card v-if="noticeDetail.noticeId" class="notice-card">
        <!-- 通知头部信息 -->
        <template #header>
          <div class="notice-header">
            <div class="notice-title-section">
              <h2 class="notice-title">{{ noticeDetail.noticeTitle }}</h2>
              <div class="notice-meta">
                <el-tag 
                  :type="getNoticeTypeTag(noticeDetail.noticeType)" 
                  class="notice-type-tag"
                >
                  {{ getNoticeTypeText(noticeDetail.noticeType) }}
                </el-tag>
                <span class="notice-date">{{ formatDate(noticeDetail.createTime) }}</span>
                <span class="notice-author">发布者：{{ noticeDetail.createBy }}</span>
              </div>
            </div>
          </div>
        </template>

        <!-- 通知内容 -->
        <div class="notice-content">
          <div v-html="noticeDetail.noticeContent" class="content-html"></div>
        </div>
      </el-card>

      <!-- 空状态 -->
      <el-empty v-else description="未找到通知详情" />

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        <el-button 
          @click="goPrevious" 
          :disabled="!hasPrevious"
          icon="ArrowUp"
        >
          上一条
        </el-button>
        <el-button 
          @click="goNext" 
          :disabled="!hasNext"
          icon="ArrowDown"
        >
          下一条
        </el-button>
      </div>

      <!-- 相关通知列表 -->
      <el-card v-if="relatedNotices.length > 0" class="related-notices-card">
        <template #header>
          <span>更多通知</span>
        </template>
        <div class="related-notices">
          <div 
            v-for="notice in relatedNotices" 
            :key="notice.noticeId"
            class="related-notice-item"
            :class="{ 'current': notice.noticeId === currentNoticeId }"
            @click="viewNotice(notice.noticeId)"
          >
            <div class="related-notice-title">{{ notice.noticeTitle }}</div>
            <div class="related-notice-meta">
              <el-tag size="small" :type="getNoticeTypeTag(notice.noticeType)">
                {{ getNoticeTypeText(notice.noticeType) }}
              </el-tag>
              <span class="related-notice-date">{{ formatDate(notice.createTime) }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup name="NoticeDetail">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getNotice, listNotice } from '@/api/system/notice'
import { markNoticeAsRead } from '@/utils/noticeStorage'

// 路由和状态管理
const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const noticeDetail = ref({})
const relatedNotices = ref([])
const currentNoticeId = ref(null)

// 计算属性
const hasPrevious = computed(() => {
  const currentIndex = relatedNotices.value.findIndex(n => n.noticeId === currentNoticeId.value)
  return currentIndex > 0
})

const hasNext = computed(() => {
  const currentIndex = relatedNotices.value.findIndex(n => n.noticeId === currentNoticeId.value)
  return currentIndex >= 0 && currentIndex < relatedNotices.value.length - 1
})

// 获取通知详情
async function fetchNoticeDetail(noticeId) {
  loading.value = true
  try {
    const response = await getNotice(noticeId)
    noticeDetail.value = response.data || {}
    currentNoticeId.value = noticeId
    
    // 标记为已读
    markNoticeAsRead(noticeId)
    
    // 获取相关通知列表
    await fetchRelatedNotices()
    
  } catch (error) {
    console.error('获取通知详情失败:', error)
    ElMessage.error('获取通知详情失败')
  } finally {
    loading.value = false
  }
}

// 获取相关通知列表（最新的10条）
async function fetchRelatedNotices() {
  try {
    const response = await listNotice({
      pageNum: 1,
      pageSize: 10
    })
    relatedNotices.value = response.rows || []
  } catch (error) {
    console.error('获取相关通知失败:', error)
  }
}

// 查看指定通知
function viewNotice(noticeId) {
  router.push({ 
    name: 'NoticeDetail', 
    params: { id: noticeId }
  })
  fetchNoticeDetail(noticeId)
}

// 导航方法
function goBack() {
  router.back()
}

function goPrevious() {
  const currentIndex = relatedNotices.value.findIndex(n => n.noticeId === currentNoticeId.value)
  if (currentIndex > 0) {
    const previousNotice = relatedNotices.value[currentIndex - 1]
    viewNotice(previousNotice.noticeId)
  }
}

function goNext() {
  const currentIndex = relatedNotices.value.findIndex(n => n.noticeId === currentNoticeId.value)
  if (currentIndex >= 0 && currentIndex < relatedNotices.value.length - 1) {
    const nextNotice = relatedNotices.value[currentIndex + 1]
    viewNotice(nextNotice.noticeId)
  }
}

// 工具方法
function getNoticeTypeText(type) {
  return type === '1' ? '通知' : '公告'
}

function getNoticeTypeTag(type) {
  return type === '1' ? 'warning' : 'success'
}

function formatDate(dateStr) {
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

// 组件挂载时获取通知详情
onMounted(() => {
  const noticeId = route.params.id
  if (noticeId) {
    fetchNoticeDetail(parseInt(noticeId))
  } else {
    ElMessage.error('通知ID无效')
    router.back()
  }
})
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.breadcrumb-container {
  margin-bottom: 20px;
}

.notice-detail-container {
  max-width: 1000px;
  margin: 0 auto;
}

.notice-card {
  margin-bottom: 20px;
  
  .notice-header {
    .notice-title-section {
      .notice-title {
        margin: 0 0 12px 0;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        line-height: 1.4;
      }
      
      .notice-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 14px;
        color: #606266;
        
        .notice-type-tag {
          font-size: 12px;
        }
        
        .notice-date {
          color: #909399;
        }
        
        .notice-author {
          color: #909399;
        }
      }
    }
  }
}

.notice-content {
  .content-html {
    font-size: 16px;
    line-height: 1.8;
    color: #303133;
    min-height: 200px;
    
    // 富文本内容样式优化
    :deep(p) {
      margin-bottom: 12px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    :deep(img) {
      max-width: 100%;
      height: auto;
      border-radius: 4px;
    }
    
    :deep(table) {
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0;
      
      th,
      td {
        border: 1px solid #dcdfe6;
        padding: 8px 12px;
        text-align: left;
      }
      
      th {
        background-color: #f5f7fa;
        font-weight: 600;
      }
    }
  }
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 20px 0;
}

.related-notices-card {
  .related-notices {
    .related-notice-item {
      padding: 12px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.3s ease;
      border: 1px solid transparent;
      
      &:hover {
        background-color: #f5f7fa;
        border-color: #e4e7ed;
      }
      
      &.current {
        background-color: #ecf5ff;
        border-color: #b3d8ff;
      }
      
      &:not(:last-child) {
        margin-bottom: 8px;
      }
      
      .related-notice-title {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 6px;
        line-height: 1.4;
        
        // 文本溢出省略
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .related-notice-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        
        .related-notice-date {
          color: #909399;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .app-container {
    padding: 12px;
  }
  
  .notice-detail-container {
    max-width: 100%;
  }
  
  .notice-card {
    .notice-header {
      .notice-title-section {
        .notice-title {
          font-size: 20px;
        }
        
        .notice-meta {
          flex-direction: column;
          align-items: flex-start;
          gap: 8px;
        }
      }
    }
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>
