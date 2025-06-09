import request from '@/utils/request'

// 查询设备列表
export function listDevice(query) {
  return request({
    url: '/redfish/device/list',
    method: 'get',
    params: query
  })
}

// 查询设备详细
export function getDevice(deviceId, forEdit = false) {
  return request({
    url: '/redfish/device/' + deviceId,
    method: 'get',
    params: forEdit ? { forEdit: true } : {}
  })
}

// 新增设备
export function addDevice(data) {
  return request({
    url: '/redfish/device',
    method: 'post',
    data: data
  })
}

// 修改设备
export function updateDevice(data) {
  return request({
    url: '/redfish/device',
    method: 'put',
    data: data
  })
}

// 删除设备
export function delDevice(deviceId) {
  return request({
    url: '/redfish/device/' + deviceId,
    method: 'delete'
  })
}



// 通过设备ID测试连接
export function testConnectionById(deviceId) {
  return request({
    url: '/redfish/device/testConnectionById',
    method: 'post',
    data: { deviceId }
  })
}

// 获取设备统计信息
export function getDeviceStatistics() {
  return request({
    url: '/redfish/device/statistics',
    method: 'get'
  })
}

// 获取监控设备列表
export function getMonitoringDevices() {
  return request({
    url: '/redfish/device/monitoring/list',
    method: 'get'
  })
}

// 修改设备状态
export function changeDeviceStatus(deviceId, status) {
  const data = {
    deviceId,
    status
  }
  return request({
    url: '/redfish/device/changeStatus',
    method: 'put',
    data: data
  })
}

// 修改监控状态
export function changeMonitorStatus(deviceId, monitorEnabled) {
  const data = {
    deviceId,
    monitorEnabled
  }
  return request({
    url: '/redfish/device/changeMonitoring',
    method: 'put',
    data: data
  })
}

// 导出设备
export function exportDevice(query) {
  return request({
    url: '/redfish/device/export',
    method: 'get',
    params: query
  })
} 