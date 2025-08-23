import request from '@/utils/request'

// 获取日志列表
export function listRedfishLog(query) {
  return request({
    url: '/redfish/log/list',
    method: 'get',
    params: query
  })
}

// 获取日志统计信息
export function getRedfishLogStatistics() {
  return request({
    url: '/redfish/log/statistics',
    method: 'get'
  })
}

// 获取日志详情
export function getRedfishLog(logId) {
  return request({
    url: '/redfish/log/' + logId,
    method: 'get'
  })
}

// 收集设备日志
export function collectDeviceLogs(data) {
  return request({
    url: '/redfish/log/collect',
    method: 'post',
    data: data
  })
}

// 清理旧日志
export function cleanupOldLogs(days) {
  return request({
    url: '/redfish/log/cleanup',
    method: 'post',
    params: { days: days }
  })
}

// 删除日志
export function delRedfishLog(logId) {
  return request({
    url: '/redfish/log/' + logId,
    method: 'delete'
  })
}

// 删除指定设备的所有日志
export function delDeviceLogs(deviceId) {
  return request({
    url: '/redfish/log/device/' + deviceId,
    method: 'delete'
  })
}

// 导出日志数据
export function exportLogsData(query) {
  return request({
    url: '/redfish/log/export/data',
    method: 'get',
    params: query
  })
}

// 获取设备列表（用于下拉选择）
export function getDeviceSelectList() {
  return request({
    url: '/redfish/device/list',
    method: 'get',
    params: { pageSize: 1000 }
  })
}
