<template>
  <div class="dashboard-container">
    <!-- 连接状态和控制区域 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="24">
        <el-card class="status-card">
          <div class="status-content">
            <div class="connection-status">
              <el-icon :class="wsConnected ? 'connected' : 'disconnected'">
                <CircleCheck v-if="wsConnected" />
                <CircleClose v-else />
              </el-icon>
              <span :class="wsConnected ? 'connected-text' : 'disconnected-text'">
                {{ wsConnected ? '实时连接已建立' : '实时连接断开' }}
              </span>
            </div>
            
            <!-- 监控进度显示 -->
            <div v-if="monitoringProgress.isMonitoring" class="monitoring-progress">
              <el-progress 
                :percentage="monitoringProgress.progress" 
                :status="monitoringProgress.progress === 100 ? 'success' : undefined"
                :stroke-width="8"
              />
              <div class="progress-info">
                正在监控: {{ monitoringProgress.currentDevice }} 
                ({{ monitoringProgress.completed }}/{{ monitoringProgress.total }})
              </div>
            </div>
            
            <!-- 手动触发按钮 -->
            <div class="manual-controls">
              <el-button 
                type="primary" 
                :disabled="!wsConnected || monitoringProgress.isMonitoring"
                @click="triggerManualMonitoring"
              >
                <el-icon><Refresh /></el-icon>
                手动监控
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 统计卡片区域 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon devices">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ overviewData.totalDevices }}</div>
              <div class="stat-label">总设备数</div>
              <div class="stat-detail">
                在线: {{ overviewData.onlineDevices }} | 离线: {{ overviewData.offlineDevices }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon alerts-7d">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ overviewData.alerts7Days }}</div>
              <div class="stat-label">7天告警</div>
              <div class="stat-detail">
                紧急: {{ overviewData.urgentAlerts7Days }} | 择期: {{ overviewData.scheduledAlerts7Days }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon alerts-30d">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ overviewData.alerts30Days }}</div>
              <div class="stat-label">30天告警</div>
              <div class="stat-detail">
                紧急: {{ overviewData.urgentAlerts30Days }} | 择期: {{ overviewData.scheduledAlerts30Days }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon current-alerts">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ overviewData.currentUrgentAlerts + overviewData.currentScheduledAlerts }}</div>
              <div class="stat-label">当前告警</div>
              <div class="stat-detail">
                紧急: {{ overviewData.currentUrgentAlerts }} | 择期: {{ overviewData.currentScheduledAlerts }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 告警列表区域 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>紧急告警列表</span>
              <el-button link @click="refreshRealtimeAlerts">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="realtimeAlerts" style="width: 100%" max-height="400">
            <el-table-column prop="hostname" label="设备名称" width="120" show-overflow-tooltip />
            <el-table-column prop="componentType" label="组件类型" width="90" />
            <el-table-column prop="componentName" label="组件名称" width="100" show-overflow-tooltip />
            <el-table-column prop="healthStatus" label="健康状态" width="90">
              <template #default="scope">
                <el-tag :type="getHealthStatusType(scope.row.healthStatus)" size="small">
                  {{ getHealthStatusText(scope.row.healthStatus) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="urgencyLevel" label="紧急程度" width="90">
              <template #default="scope">
                <el-tag :type="getUrgencyLevelType(scope.row.urgencyLevel)" size="small">
                  {{ getUrgencyLevelText(scope.row.urgencyLevel) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="firstOccurrence" label="发生时间" width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.firstOccurrence) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>择期告警列表</span>
              <el-button link @click="refreshScheduledAlerts">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="scheduledAlerts" style="width: 100%" max-height="400">
            <el-table-column prop="hostname" label="设备名称" width="120" show-overflow-tooltip />
            <el-table-column prop="componentType" label="组件类型" width="90" />
            <el-table-column prop="componentName" label="组件名称" width="100" show-overflow-tooltip />
            <el-table-column prop="healthStatus" label="健康状态" width="90">
              <template #default="scope">
                <el-tag :type="getHealthStatusType(scope.row.healthStatus)" size="small">
                  {{ getHealthStatusText(scope.row.healthStatus) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="urgencyLevel" label="紧急程度" width="90">
              <template #default="scope">
                <el-tag :type="getUrgencyLevelType(scope.row.urgencyLevel)" size="small">
                  {{ getUrgencyLevelText(scope.row.urgencyLevel) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="firstOccurrence" label="发生时间" width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.firstOccurrence) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>


    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>告警趋势图</span>
              <el-radio-group v-model="trendDays" @change="loadTrendChart">
                <el-radio-button :value="7">7天</el-radio-button>
                <el-radio-button :value="30">30天</el-radio-button>
                <el-radio-button :value="90">90天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>设备健康图</span>
          </template>
          <div ref="healthChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
  </div>
</template>

<script setup name="RedfishDashboard">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Monitor, Warning, Bell, CircleClose, CircleCheck, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getDashboardOverview, getAlertTrend, getDeviceHealth, getRealtimeAlerts, getScheduledAlerts } from '@/api/redfish/dashboard'
import { triggerMonitor } from '@/api/redfish/monitor'
import websocketService from '@/utils/websocket'
import { ElNotification, ElMessage } from 'element-plus'

// 响应式数据
const overviewData = ref({
  totalDevices: 0,
  onlineDevices: 0,
  offlineDevices: 0,
  healthyDevices: 0,
  warningDevices: 0,
  criticalDevices: 0,
  alerts7Days: 0,
  urgentAlerts7Days: 0,
  scheduledAlerts7Days: 0,
  alerts30Days: 0,
  urgentAlerts30Days: 0,
  scheduledAlerts30Days: 0,
  currentUrgentAlerts: 0,
  currentScheduledAlerts: 0
})

const trendDays = ref(7)
const realtimeAlerts = ref([])
const scheduledAlerts = ref([])

// WebSocket连接状态
const wsConnected = ref(false)
const wsConnecting = ref(false)

// 监控进度状态
const monitoringProgress = ref({
  isMonitoring: false,
  completed: 0,
  total: 0,
  progress: 0,
  currentDevice: ''
})

// 图表引用
const trendChartRef = ref(null)
const healthChartRef = ref(null)
let trendChart = null
let healthChart = null

// ===============================================================
// 数据加载函数
// ===============================================================
const loadDashboardData = async () => {
  await Promise.all([
    loadOverviewData(),
    loadRealtimeAlerts(),
    loadScheduledAlerts(),
    loadTrendChart(),
    loadHealthChart()
  ]);
};

const loadOverviewData = async () => {
  try {
    const response = await getDashboardOverview('7d')
    if (response.success) {
      overviewData.value = response.data
    }
  } catch (error) {
    console.error('加载概览数据失败:', error)
  }
}

// 加载趋势图
const loadTrendChart = async () => {
  try {
    const response = await getAlertTrend(trendDays.value)
    if (response.success && trendChart) {
      const data = response.data
      
      const option = {
        title: {
          text: `${trendDays.value}天告警趋势`,
          left: 'center',
          textStyle: {
            fontSize: 14
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['紧急告警', '择期告警', '总告警'],
          bottom: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: data.dates
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '紧急告警',
            type: 'line',
            data: data.urgentCounts,
            itemStyle: { color: '#f56c6c' },
            smooth: true
          },
          {
            name: '择期告警',
            type: 'line',
            data: data.scheduledCounts,
            itemStyle: { color: '#e6a23c' },
            smooth: true
          },
          {
            name: '总告警',
            type: 'line',
            data: data.totalCounts,
            itemStyle: { color: '#409eff' },
            smooth: true
          }
        ]
      }
      
      trendChart.setOption(option)
    }
  } catch (error) {
    console.error('加载趋势图失败:', error)
  }
}

// 加载设备健康图
const loadHealthChart = async () => {
  try {
    const response = await getDeviceHealth()
    if (response.success && healthChart) {
      const data = response.data
      
      const option = {
        title: {
          text: '设备健康状态',
          left: 'center',
          textStyle: {
            fontSize: 14
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: ['正常', '警告', '未知']
        },
        series: [
          {
            name: '设备健康状态',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
            data: [
              { value: data.healthyCount, name: '正常', itemStyle: { color: '#67c23a' } },
              { value: data.warningCount, name: '警告', itemStyle: { color: '#e6a23c' } },
              { value: data.offlineCount, name: '未知', itemStyle: { color: '#909399' } }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      
      healthChart.setOption(option)
    }
  } catch (error) {
    console.error('加载设备健康图失败:', error)
  }
}

// 加载实时告警列表
const loadRealtimeAlerts = async () => {
  try {
    const response = await getRealtimeAlerts(10)
    if (response.success) {
      realtimeAlerts.value = response.data
    }
  } catch (error) {
    console.error('加载实时告警列表失败:', error)
  }
}

// 加载择期告警列表
const loadScheduledAlerts = async () => {
  try {
    const response = await getScheduledAlerts(10)
    if (response.success) {
      scheduledAlerts.value = response.data
    }
  } catch (error) {
    console.error('加载择期告警列表失败:', error)
  }
}

// 刷新实时告警
const refreshRealtimeAlerts = () => {
  loadRealtimeAlerts()
}

// 刷新择期告警
const refreshScheduledAlerts = () => {
  loadScheduledAlerts()
}

// 获取健康状态类型
const getHealthStatusType = (status) => {
  const statusMap = {
    'ok': 'success',
    'warning': 'warning',
    'critical': 'warning',
    'unknown': 'info'
  }
  return statusMap[status] || 'info'
}

// 获取健康状态文本
const getHealthStatusText = (status) => {
  const statusMap = {
    'ok': '正常',
    'warning': '警告',
    'critical': '警告',
    'unknown': '未知'
  }
  return statusMap[status] || '未知'
}

// 获取紧急程度类型
const getUrgencyLevelType = (level) => {
  const levelMap = {
    'urgent': 'danger',
    'scheduled': 'warning'
  }
  return levelMap[level] || 'info'
}

// 获取紧急程度文本
const getUrgencyLevelText = (level) => {
  const levelMap = {
    'urgent': '紧急',
    'scheduled': '择期'
  }
  return levelMap[level] || '未知'
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 初始化图表
const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      trendChart = echarts.init(trendChartRef.value)
      loadTrendChart()
    }
    
    if (healthChartRef.value) {
      healthChart = echarts.init(healthChartRef.value)
      loadHealthChart()
    }
  })
}

// WebSocket事件处理函数
const handleWebSocketConnection = (data) => {
  wsConnected.value = data.is_connected;
};

const handleAlert = (alertData) => {
  const action = alertData.action || 'created'
  const actionText = action === 'created' ? '新告警' : '告警更新'
  
  // 对于单个告警变化，显示通知但主要依靠告警列表刷新来更新数据
  ElMessage({
    message: `${alertData.hostname}: ${actionText} - ${alertData.alert_message}`,
    type: alertData.urgency_level === 'urgent' ? 'error' : 'warning',
    duration: 5000,
    showClose: true
  })
  
  // 刷新告警列表以确保数据最新
  loadRealtimeAlerts()
  loadScheduledAlerts()
  
  // 刷新概览数据
  loadOverviewData()
  
  // 重新加载图表数据
  loadTrendChart()
  loadHealthChart()
}

const handleDeviceStatusChange = (data) => {
  // 立即刷新概览数据
  loadOverviewData()
  
  // 如果有设备健康状态变化，更新图表
  loadTrendChart()
  loadHealthChart()
  
  // 设备健康状态变化已静默处理，不显示用户通知
  
  // 只在有告警相关变化时重新加载告警列表
  if (data.hostname && data.old_status && data.new_status) {
    // 如果状态变坏了，重新加载告警列表
    if (data.new_status !== 'ok' && data.old_status === 'ok') {
      loadRealtimeAlerts()
      loadScheduledAlerts()
    }
    // 如果状态恢复正常，也重新加载以移除可能解决的告警
    else if (data.new_status === 'ok' && data.old_status !== 'ok') {
      loadRealtimeAlerts()
      loadScheduledAlerts()
    }
  }
}

const handleMonitoringStarted = (data) => {
  // 只在未监控状态时显示通知，避免重复
  const wasMonitoring = monitoringProgress.value.isMonitoring
  
  // 设置监控开始状态
  monitoringProgress.value.isMonitoring = true
  monitoringProgress.value.completed = 0
  monitoringProgress.value.total = data.results?.total_devices || 0
  monitoringProgress.value.progress = 0
  monitoringProgress.value.currentDevice = '监控已开始...'
  
  // 只在首次开始时显示通知，避免重复
  if (!wasMonitoring) {
    ElMessage.success(`开始监控 ${data.results?.total_devices || 0} 台设备`)
  }
}

const handleMonitoringCompleted = (data) => {
  // 重置监控进度
  monitoringProgress.value.isMonitoring = false
  monitoringProgress.value.completed = 0
  monitoringProgress.value.total = 0
  monitoringProgress.value.progress = 0
  monitoringProgress.value.currentDevice = ''
  
  // 刷新所有数据
  loadOverviewData()
  loadRealtimeAlerts()
  loadScheduledAlerts()
  loadTrendChart()
  loadHealthChart()
  
  // 显示监控完成通知
  const totalDevices = data.results?.total_devices || 0
  const successDevices = data.results?.successful_devices || 0
  const failedDevices = data.results?.failed_devices || 0
  
  let message = `监控完成：${totalDevices} 台设备`
  if (failedDevices > 0) {
    message += ` (${successDevices} 成功, ${failedDevices} 失败)`
  }
  
  ElNotification({
    title: '监控完成',
    message: message,
    type: failedDevices > 0 ? 'warning' : 'success',
    duration: 4000
  })
}

const handleMonitoringProgress = (data) => {
  monitoringProgress.value.isMonitoring = true
  monitoringProgress.value.completed = data.completed || 0
  monitoringProgress.value.total = data.total || 0
  monitoringProgress.value.progress = data.progress || 0
  monitoringProgress.value.currentDevice = data.current_device || ''
}

const handleDashboardUpdate = (message) => {
  // 处理告警列表刷新消息（来自定时任务的告警变化）
  if (message.action === 'alert_list_refresh' && message.data) {
    const { device_id, hostname, alert_changes, new_alerts, updated_alerts } = message.data
    
    // 立即刷新告警列表和概览数据
    Promise.all([
      loadRealtimeAlerts().catch(err => console.error('[Dashboard] Failed to load realtime alerts:', err)),
      loadScheduledAlerts().catch(err => console.error('[Dashboard] Failed to load scheduled alerts:', err)),
      loadOverviewData().catch(err => console.error('[Dashboard] Failed to load overview data:', err))
    ]).catch(err => {
      console.error('[Dashboard] Data refresh error:', err)
    })
    
    // 显示告警变化通知
    if (alert_changes > 0) {
      let message = `设备 ${hostname} 告警状态已更新`
      if (new_alerts > 0 && updated_alerts > 0) {
        message += ` (${new_alerts}条新告警, ${updated_alerts}条更新)`
      } else if (new_alerts > 0) {
        message += ` (${new_alerts}条新告警)`
      } else if (updated_alerts > 0) {
        message += ` (${updated_alerts}条告警更新)`
      }
      
      ElMessage({
        message,
        type: new_alerts > 0 ? 'warning' : 'info',
        duration: 4000,
        showClose: true
      })
    }
    
    // 更新图表
    loadTrendChart()
    loadHealthChart()
    return
  }
  
  // 处理设备更新消息（来自定时任务的健康状态更新）
  if (message.action === 'device_updated' && message.data) {
    const { device_id, hostname, health_status, alert_count, has_health_change, has_alert_changes } = message.data
    
    // 立即刷新概览数据
    loadOverviewData()
    
    // 如果有告警变化，刷新告警列表
    if (has_alert_changes || alert_count > 0) {
      loadRealtimeAlerts()
      loadScheduledAlerts()
    }
    
    // 更新图表
    loadTrendChart()
    loadHealthChart()
    return
  }
  
  // 如果是刷新请求，重新加载所有数据
  if (message.type === 'data_refresh' || message.type === 'manual_refresh' || message.action === 'refresh_all') {
    loadOverviewData()
    loadRealtimeAlerts()
    loadScheduledAlerts()
    loadTrendChart()
    loadHealthChart()
    return
  }
  
  // 处理完整数据更新
  if (message.action === 'full_data_update' && message.data) {
    const { statistics, realtime_alerts, scheduled_alerts_list } = message.data
    
    // 更新概览数据
    if (statistics) {
      overviewData.value = {
        totalDevices: statistics.total_devices || 0,
        alerts7d: statistics.alerts_7d || 0,
        alerts30d: statistics.alerts_30d || 0,
        urgentAlerts: statistics.urgent_alerts || 0,
        scheduledAlerts: statistics.scheduled_alerts || 0,
        healthDistribution: statistics.health_distribution || { healthy: 0, warning: 0, critical: 0, unknown: 0 }
      }
    }
    
    // 更新实时告警列表
    if (realtime_alerts) {
      realtimeAlerts.value = realtime_alerts
    }
    
    // 更新择期告警列表
    if (scheduled_alerts_list) {
      scheduledAlerts.value = scheduled_alerts_list
    }
    
    // 更新图表
    loadTrendChart()
    loadHealthChart()
    return
  }
  
  // 如果有概览数据更新，直接使用
  if (message.overview) {
    overviewData.value = { ...overviewData.value, ...message.overview }
  }
  
  // 如果有告警列表更新，直接使用
  if (message.realtimeAlerts) {
    realtimeAlerts.value = message.realtimeAlerts
  }
  
  if (message.scheduledAlerts) {
    scheduledAlerts.value = message.scheduledAlerts
  }
}

// 处理告警统计更新
const handleAlertStatisticsUpdate = (statistics) => {
  if (statistics) {
    overviewData.value = {
      ...overviewData.value,
      totalDevices: statistics.total_devices || overviewData.value.totalDevices,
      alerts7d: statistics.alerts_7d || overviewData.value.alerts7d,
      alerts30d: statistics.alerts_30d || overviewData.value.alerts30d,
      urgentAlerts: statistics.urgent_alerts || overviewData.value.urgentAlerts,
      scheduledAlerts: statistics.scheduled_alerts || overviewData.value.scheduledAlerts,
      healthDistribution: statistics.health_distribution || overviewData.value.healthDistribution
    }
    // 更新图表
    loadTrendChart()
    loadHealthChart()
  }
}

// 处理设备健康状态汇总
const handleDeviceHealthSummary = (devices) => {
  loadOverviewData()
}

// 处理设备健康状态静默更新（仅更新健康图）
const handleHealthStatusSilentUpdate = (data) => {
  if (data && data.device_id) {
    // 只更新健康图表，不显示用户通知，不更新告警列表
    loadHealthChart()
    
    // 更新概览数据中的健康状态统计
    loadOverviewData().catch(err => {
      console.error('[Dashboard] Failed to update health chart:', err)
    })
  }
}

// 处理Dashboard统计数据
const handleDashboardStatistics = (statistics) => {
  handleAlertStatisticsUpdate(statistics)
}

// 处理监控任务状态更新
const handleMonitoringTaskStatus = (data) => {
  console.log("Monitoring task status update:", data);
  // 这里可以根据需要更新UI，例如显示一个全局的加载状态
};

const handleUrgencyRecalculation = async (data) => {
  console.log("Urgency recalculation completed, starting data refresh:", data);
  ElNotification({
    title: '数据更新',
    message: data.message || '部分告警的紧急度已更新，正在刷新仪表盘...',
    type: 'info',
    duration: 3000
  });
  await loadDashboardData();
};

// 设置WebSocket事件监听器
const setupWebSocketListeners = () => {
  websocketService.on('connection', handleWebSocketConnection)
  websocketService.on('new_alert', handleAlert)
  websocketService.on('device_status_change', handleDeviceStatusChange)
  websocketService.on('monitoring_started', handleMonitoringStarted)
  websocketService.on('monitoring_completed', handleMonitoringCompleted)
  websocketService.on('monitoring_progress', handleMonitoringProgress)
  websocketService.on('dashboard_update', handleDashboardUpdate)
  websocketService.on('health_status_silent_update', handleHealthStatusSilentUpdate)
  websocketService.on('alert_statistics_update', handleAlertStatisticsUpdate)
  websocketService.on('device_health_summary', handleDeviceHealthSummary)
  websocketService.on('dashboard_statistics', handleDashboardStatistics)
  websocketService.on('monitoring_task_status', handleMonitoringTaskStatus)
  websocketService.on('urgency_recalculation_completed', handleUrgencyRecalculation)
}

// 清理WebSocket事件监听器
const cleanupWebSocketListeners = () => {
  websocketService.off('connection', handleWebSocketConnection)
  websocketService.off('new_alert', handleAlert)
  websocketService.off('device_status_change', handleDeviceStatusChange)
  websocketService.off('monitoring_started', handleMonitoringStarted)
  websocketService.off('monitoring_completed', handleMonitoringCompleted)
  websocketService.off('monitoring_progress', handleMonitoringProgress)
  websocketService.off('dashboard_update', handleDashboardUpdate)
  websocketService.off('health_status_silent_update', handleHealthStatusSilentUpdate)
  websocketService.off('alert_statistics_update', handleAlertStatisticsUpdate)
  websocketService.off('device_health_summary', handleDeviceHealthSummary)
  websocketService.off('dashboard_statistics', handleDashboardStatistics)
  websocketService.off('monitoring_task_status', handleMonitoringTaskStatus)
  websocketService.off('urgency_recalculation_completed', handleUrgencyRecalculation)
}

// 手动触发监控
const triggerManualMonitoring = async () => {
  try {
    // 优先使用HTTP API方式触发监控
    const response = await triggerMonitor(false)
    
    if (response.success) {
      // 移除重复通知，监控开始时会有专门的通知
      // ElMessage.success('监控任务已成功触发')
      
      // 设置监控中状态
      monitoringProgress.value.isMonitoring = true
      monitoringProgress.value.progress = 0
      monitoringProgress.value.currentDevice = '准备开始...'
      
      // 移除WebSocket触发，避免重复执行
      // WebSocket连接主要用于接收监控状态更新，不用于触发监控
    } else {
      ElMessage.error(response.msg || '触发监控失败')
    }
  } catch (error) {
    console.error('手动触发监控失败:', error)
    ElMessage.error('触发监控失败，请稍后重试')
  }
}

// ===============================================================
// 生命周期钩子
// ===============================================================
onMounted(() => {
  initCharts()
  loadDashboardData()
  
  // 设置WebSocket事件监听
  setupWebSocketListeners()
  
  // 主动检查WebSocket连接状态
  wsConnected.value = websocketService.isConnected()
  
  // 如果未连接，尝试重新连接
  if (!wsConnected.value) {
    console.log('[Dashboard] WebSocket未连接，尝试重新连接...')
    websocketService.connect()
  } else {
    console.log('[Dashboard] WebSocket已连接')
  }
});

  onUnmounted(() => {
    // 清理图表
    if (trendChart) {
      trendChart.dispose()
    }
    if (healthChart) {
      healthChart.dispose()
    }
    
    // 清理WebSocket事件监听器
    cleanupWebSocketListeners()
});
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.mb-20 {
  margin-bottom: 20px;
}

/* 状态卡片样式 */
.status-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.status-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
}

/* 连接状态样式 */
.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.connection-status .el-icon {
  font-size: 20px;
}

.connection-status .el-icon.connected {
  color: #67c23a;
}

.connection-status .el-icon.disconnected {
  color: #f56c6c;
}

.connected-text {
  color: #67c23a;
  font-weight: 600;
}

.disconnected-text {
  color: #f56c6c;
  font-weight: 600;
}

/* 监控进度样式 */
.monitoring-progress {
  flex: 1;
  max-width: 400px;
  margin: 0 20px;
}

.progress-info {
  text-align: center;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

/* 手动控制样式 */
.manual-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stat-icon.devices {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.alerts-7d {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.alerts-30d {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.current-alerts {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 4px;
}

.stat-detail {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-card__header) {
  padding: 12px 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-table) {
  font-size: 12px;
}

:deep(.el-table .cell) {
  padding: 0 8px;
}
</style> 