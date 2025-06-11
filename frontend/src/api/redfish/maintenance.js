import request from '@/utils/request'

// 查询维护排期列表
export function listMaintenance(query) {
  return request({
    url: '/redfish/maintenance/list',
    method: 'get',
    params: query
  })
}

// 查询维护排期详细
export function getMaintenance(alertId) {
  return request({
    url: '/redfish/maintenance/detail/' + alertId,
    method: 'get'
  })
}

// 新增维护排期
export function addMaintenance(data) {
  return request({
    url: '/redfish/maintenance/add',
    method: 'post',
    data: data
  })
}

// 修改维护排期
export function updateMaintenance(data) {
  return request({
    url: '/redfish/maintenance/edit',
    method: 'put',
    data: data
  })
}

// 删除维护排期
export function delMaintenance(alertId) {
  return request({
    url: '/redfish/maintenance/delete/' + alertId,
    method: 'delete'
  })
}

// 获取维护排期统计信息
export function getMaintenanceStatistics() {
  return request({
    url: '/redfish/maintenance/statistics',
    method: 'get'
  })
}

// 获取维护排期日历数据
export function getMaintenanceCalendar(year, month) {
  return request({
    url: '/redfish/maintenance/calendar',
    method: 'get',
    params: { year, month }
  })
}

// 批量更新维护排期
export function batchUpdateMaintenance(data) {
  return request({
    url: '/redfish/maintenance/batch-update',
    method: 'post',
    data: data
  })
}

// 获取紧急程度选项
export function getUrgencyLevelOptions() {
  return request({
    url: '/redfish/maintenance/urgency-options',
    method: 'get'
  })
}

// 从告警自动创建维护排期
export function autoCreateScheduleFromAlert(alertId) {
  return request({
    url: '/redfish/maintenance/auto-create/' + alertId,
    method: 'post'
  })
}

// 生成维护排期报告
export function generateMaintenanceReport(startDate, endDate) {
  return request({
    url: '/redfish/maintenance/report',
    method: 'get',
    params: { start_date: startDate, end_date: endDate }
  })
}

// 导出维护排期
export function exportMaintenance(query) {
  return request({
    url: '/redfish/maintenance/export',
    method: 'get',
    params: query
  })
}

// 获取设备列表（用于下拉选择）
export function listDevice(query) {
  return request({
    url: '/redfish/device/list',
    method: 'get',
    params: query
  })
} 