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

// 移除手动解决、忽略和覆盖告警功能，告警状态由监控系统自动管理

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

// 安排维修时间
export function scheduleMaintenance(data) {
  return request({
    url: '/redfish/alert/schedule-maintenance',
    method: 'post',
    data: data
  })
}

// 更新维修计划
export function updateMaintenance(data) {
  return request({
    url: '/redfish/alert/update-maintenance',
    method: 'put',
    data: data
  })
}

// 批量安排维修时间
export function batchScheduleMaintenance(data) {
  return request({
    url: '/redfish/alert/batch-schedule-maintenance',
    method: 'put',
    data: data
  })
}

// 获取维修计划列表
export function getMaintenanceSchedule(params) {
  return request({
    url: '/redfish/alert/maintenance-schedule',
    method: 'get',
    params: params
  })
}

// 取消维修计划
export function cancelMaintenance(alertId) {
  return request({
    url: `/redfish/alert/cancel-maintenance/${alertId}`,
    method: 'delete'
  })
}

// 获取日历视图的维修计划数据
export function getCalendarMaintenance(startDate, endDate) {
  return request({
    url: '/redfish/alert/calendar-maintenance',
    method: 'get',
    params: {
      start_date: startDate,
      end_date: endDate
    }
  })
} 