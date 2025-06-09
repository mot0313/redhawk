<template>
  <div class="dashboard-container">
    <!-- 统计卡片区域 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon devices">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ overviewData.total_devices }}</div>
              <div class="stat-label">总设备数</div>
              <div class="stat-detail">
                在线: {{ overviewData.online_devices }} | 离线: {{ overviewData.offline_devices }}
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
              <div class="stat-number">{{ overviewData.alerts_7days }}</div>
              <div class="stat-label">7天告警</div>
              <div class="stat-detail">
                紧急: {{ overviewData.urgent_alerts_7days }} | 择期: {{ overviewData.scheduled_alerts_7days }}
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
              <div class="stat-number">{{ overviewData.alerts_30days }}</div>
              <div class="stat-label">30天告警</div>
              <div class="stat-detail">
                紧急: {{ overviewData.urgent_alerts_30days }} | 择期: {{ overviewData.scheduled_alerts_30days }}
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
              <div class="stat-number">{{ overviewData.current_urgent_alerts + overviewData.current_scheduled_alerts }}</div>
              <div class="stat-label">当前告警</div>
              <div class="stat-detail">
                紧急: {{ overviewData.current_urgent_alerts }} | 择期: {{ overviewData.current_scheduled_alerts }}
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
              <span>实时告警列表</span>
              <el-button type="text" @click="refreshRealtimeAlerts">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="realtimeAlerts" style="width: 100%" max-height="400">
            <el-table-column prop="hostname" label="主机名" width="120" show-overflow-tooltip />
            <el-table-column prop="location" label="位置" width="100" show-overflow-tooltip />
            <el-table-column prop="component_type" label="组件" width="80" />
            <el-table-column prop="health_status" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="getHealthStatusType(scope.row.health_status)" size="small">
                  {{ getHealthStatusText(scope.row.health_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="alert_message" label="告警信息" show-overflow-tooltip />
            <el-table-column prop="duration" label="持续时间" width="100" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>择期告警列表</span>
              <el-button type="text" @click="refreshScheduledAlerts">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="scheduledAlerts" style="width: 100%" max-height="400">
            <el-table-column prop="hostname" label="主机名" width="120" show-overflow-tooltip />
            <el-table-column prop="location" label="位置" width="100" show-overflow-tooltip />
            <el-table-column prop="component_type" label="组件" width="80" />
            <el-table-column prop="health_status" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="getHealthStatusType(scope.row.health_status)" size="small">
                  {{ getHealthStatusText(scope.row.health_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="alert_message" label="告警信息" show-overflow-tooltip />
            <el-table-column prop="duration" label="持续时间" width="100" />
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
import { Monitor, Warning, Bell, CircleClose, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getDashboardOverview, getAlertTrend, getDeviceHealth, getRealtimeAlerts, getScheduledAlerts } from '@/api/redfish/dashboard'

// 响应式数据
const overviewData = ref({
  total_devices: 0,
  online_devices: 0,
  offline_devices: 0,
  healthy_devices: 0,
  warning_devices: 0,
  critical_devices: 0,
  alerts_7days: 0,
  urgent_alerts_7days: 0,
  scheduled_alerts_7days: 0,
  alerts_30days: 0,
  urgent_alerts_30days: 0,
  scheduled_alerts_30days: 0,
  current_urgent_alerts: 0,
  current_scheduled_alerts: 0
})

const trendDays = ref(7)
const realtimeAlerts = ref([])
const scheduledAlerts = ref([])

// 图表引用
const trendChartRef = ref(null)
const healthChartRef = ref(null)
let trendChart = null
let healthChart = null

// 加载概览数据
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
            data: data.urgent_counts,
            itemStyle: { color: '#f56c6c' },
            smooth: true
          },
          {
            name: '择期告警',
            type: 'line',
            data: data.scheduled_counts,
            itemStyle: { color: '#e6a23c' },
            smooth: true
          },
          {
            name: '总告警',
            type: 'line',
            data: data.total_counts,
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
          data: ['正常', '警告', '严重', '未知']
        },
        series: [
          {
            name: '设备健康状态',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
            data: [
              { value: data.healthy_count, name: '正常', itemStyle: { color: '#67c23a' } },
              { value: data.warning_count, name: '警告', itemStyle: { color: '#e6a23c' } },
              { value: data.critical_count, name: '严重', itemStyle: { color: '#f56c6c' } },
              { value: data.offline_count, name: '未知', itemStyle: { color: '#909399' } }
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
    'critical': 'danger',
    'unknown': 'info'
  }
  return statusMap[status] || 'info'
}

// 获取健康状态文本
const getHealthStatusText = (status) => {
  const statusMap = {
    'ok': '正常',
    'warning': '警告',
    'critical': '严重',
    'unknown': '未知'
  }
  return statusMap[status] || '未知'
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

// 页面挂载时加载数据
onMounted(() => {
  loadOverviewData()
  loadRealtimeAlerts()
  loadScheduledAlerts()
  initCharts()
  
  // 设置定时刷新
  const refreshInterval = setInterval(() => {
    loadOverviewData()
    loadRealtimeAlerts()
    loadScheduledAlerts()
  }, 30000) // 30秒刷新一次
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(refreshInterval)
    if (trendChart) {
      trendChart.dispose()
    }
    if (healthChart) {
      healthChart.dispose()
    }
  })
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.mb-20 {
  margin-bottom: 20px;
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