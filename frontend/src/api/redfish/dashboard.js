import request from '@/utils/request'

// 获取首页概览数据
export function getDashboardOverview(timeRange = '7d', forceRefresh = false) {
  return request({
    url: '/redfish/dashboard/overview',
    method: 'get',
    params: { 
      time_range: timeRange,
      forceRefresh: forceRefresh
    }
  })
}

// 获取告警趋势图数据
export function getAlertTrend(days = 7) {
  return request({
    url: '/redfish/dashboard/alert/trend',
    method: 'get',
    params: { days }
  })
}

// 获取设备健康图数据
export function getDeviceHealth() {
  return request({
    url: '/redfish/dashboard/device/health',
    method: 'get'
  })
}

// 获取实时告警列表
export function getRealtimeAlerts(limit = 10) {
  return request({
    url: '/redfish/dashboard/alert/realtime',
    method: 'get',
    params: { limit }
  })
}

// 获取择期告警列表
export function getScheduledAlerts(limit = 10) {
  return request({
    url: '/redfish/dashboard/alert/scheduled',
    method: 'get',
    params: { limit }
  })
}

// 获取设备健康汇总列表
export function getDeviceHealthSummary(limit = 20) {
  return request({
    url: '/redfish/dashboard/device/summary',
    method: 'get',
    params: { limit }
  })
}

// 获取系统健康指标
export function getSystemHealthMetrics() {
  return request({
    url: '/redfish/dashboard/metrics',
    method: 'get'
  })
}

// 获取完整的首页数据
export function getCompleteDashboardData(timeRange = '7d', forceRefresh = false) {
  return request({
    url: '/redfish/dashboard/complete',
    method: 'get',
    params: { 
      time_range: timeRange,
      forceRefresh: forceRefresh
    }
  })
}

// 刷新首页数据
export function refreshDashboardData(component = 'all', timeRange = '7d', forceRefresh = false) {
  return request({
    url: '/redfish/dashboard/refresh',
    method: 'get',
    params: { 
      component,
      time_range: timeRange,
      forceRefresh: forceRefresh
    }
  })
}

// 刷新设备状态缓存
export function refreshDeviceStatus() {
  return request({
    url: '/redfish/connectivity/refresh-cache',
    method: 'post'
  })
} 