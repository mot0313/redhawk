import request from '@/utils/request'

// 获取告警列表
export function getAlertList(params) {
  return request({
    url: '/redfish/alert/list',
    method: 'get',
    params: params
  })
}

// 获取告警详情
export function getAlertDetail(alertId) {
  return request({
    url: `/redfish/alert/${alertId}`,
    method: 'get'
  })
}

// 解决告警
export function resolveAlerts(data) {
  return request({
    url: '/redfish/alert/resolve',
    method: 'put',
    data: data
  })
}

// 忽略告警
export function ignoreAlerts(data) {
  return request({
    url: '/redfish/alert/ignore',
    method: 'put',
    data: data
  })
}

// 手动覆盖告警级别
export function overrideAlertLevel(data) {
  return request({
    url: '/redfish/alert/manualOverride',
    method: 'put',
    data: data
  })
}

// 获取告警统计信息
export function getAlertStatistics(days = 7) {
  return request({
    url: '/redfish/alert/statistics',
    method: 'get',
    params: { days }
  })
}

// 获取告警趋势数据
export function getAlertTrend(days = 7) {
  return request({
    url: '/redfish/alert/trend',
    method: 'get',
    params: { days }
  })
}

// 获取实时告警列表
export function getRealtimeAlerts(limit = 10) {
  return request({
    url: '/redfish/alert/realtime',
    method: 'get',
    params: { limit }
  })
}

// 获取择期告警列表
export function getScheduledAlerts(limit = 10) {
  return request({
    url: '/redfish/alert/scheduled',
    method: 'get',
    params: { limit }
  })
}

// 获取告警分布数据
export function getAlertDistribution() {
  return request({
    url: '/redfish/alert/distribution',
    method: 'get'
  })
}

// 获取设备告警列表
export function getDeviceAlerts(deviceId) {
  return request({
    url: `/redfish/alert/device/${deviceId}`,
    method: 'get'
  })
}

// 导出告警数据
export function exportAlerts(params) {
  return request({
    url: '/redfish/alert/export',
    method: 'get',
    params: params,
    responseType: 'blob'
  })
} 