import request from '@/utils/request'

// ==================== 业务类型管理 ====================

// 获取业务类型列表
export function listBusinessType(query) {
  return request({
    url: '/redfish/businessRule/business-types',
    method: 'get',
    params: query
  })
}

// 获取所有业务类型（不分页）
export function getAllBusinessTypes() {
  return request({
    url: '/redfish/businessRule/business-types/all',
    method: 'get'
  })
}

// 获取业务类型选项（用于下拉框）
export function getBusinessTypeOptions() {
  return request({
    url: '/redfish/businessRule/business-types/options',
    method: 'get'
  })
}

// 获取业务类型详情
export function getBusinessType(typeId) {
  return request({
    url: `/redfish/businessRule/business-types/${typeId}`,
    method: 'get'
  })
}

// 新增业务类型
export function addBusinessType(data) {
  return request({
    url: '/redfish/businessRule/business-types',
    method: 'post',
    data: data
  })
}

// 修改业务类型
export function updateBusinessType(data) {
  return request({
    url: '/redfish/businessRule/business-types',
    method: 'put',
    data: data
  })
}

// 删除业务类型
export function delBusinessType(typeIds) {
  return request({
    url: `/redfish/businessRule/business-types/${typeIds}`,
    method: 'delete'
  })
}

// ==================== 硬件类型管理 ====================

// 获取硬件类型列表
export function listHardwareType(query) {
  return request({
    url: '/redfish/businessRule/hardware-types',
    method: 'get',
    params: query
  })
}

// 获取所有硬件类型（不分页）
export function getAllHardwareTypes() {
  return request({
    url: '/redfish/businessRule/hardware-types/all',
    method: 'get'
  })
}

// 获取硬件类型选项（用于下拉框）
export function getHardwareTypeOptions() {
  return request({
    url: '/redfish/businessRule/hardware-types/options',
    method: 'get'
  })
}

// 获取硬件分类选项
export function getHardwareCategories() {
  return request({
    url: '/redfish/businessRule/hardware-types/categories',
    method: 'get'
  })
}

// 获取硬件类型详情
export function getHardwareType(typeId) {
  return request({
    url: `/redfish/businessRule/hardware-types/${typeId}`,
    method: 'get'
  })
}

// 新增硬件类型
export function addHardwareType(data) {
  return request({
    url: '/redfish/businessRule/hardware-types',
    method: 'post',
    data: data
  })
}

// 修改硬件类型
export function updateHardwareType(data) {
  return request({
    url: '/redfish/businessRule/hardware-types',
    method: 'put',
    data: data
  })
}

// 删除硬件类型
export function delHardwareType(typeIds) {
  return request({
    url: `/redfish/businessRule/hardware-types/${typeIds}`,
    method: 'delete'
  })
}

// ==================== 紧急度规则管理 ====================

// 获取紧急度规则列表
export function listUrgencyRule(query) {
  return request({
    url: '/redfish/businessRule/urgency-rules',
    method: 'get',
    params: query
  })
}

// 获取所有紧急度规则（不分页）
export function getAllUrgencyRules() {
  return request({
    url: '/redfish/businessRule/urgency-rules/all',
    method: 'get'
  })
}

// 获取紧急度规则详情
export function getUrgencyRule(ruleId) {
  return request({
    url: `/redfish/businessRule/urgency-rules/${ruleId}`,
    method: 'get'
  })
}

// 新增紧急度规则
export function addUrgencyRule(data) {
  return request({
    url: '/redfish/businessRule/urgency-rules',
    method: 'post',
    data: data
  })
}

// 修改紧急度规则
export function updateUrgencyRule(data) {
  return request({
    url: '/redfish/businessRule/urgency-rules',
    method: 'put',
    data: data
  })
}

// 删除紧急度规则
export function delUrgencyRule(ruleIds) {
  return request({
    url: `/redfish/businessRule/urgency-rules/${ruleIds}`,
    method: 'delete'
  })
}

// 查询业务规则列表
export function listBusinessRule(query) {
  return request({
    url: '/redfish/businessRule/list',
    method: 'get',
    params: query
  })
}

// 查询业务规则详细
export function getBusinessRule(ruleId) {
  return request({
    url: '/redfish/businessRule/' + ruleId,
    method: 'get'
  })
}

// 新增业务规则
export function addBusinessRule(data) {
  return request({
    url: '/redfish/businessRule',
    method: 'post',
    data: data
  })
}

// 修改业务规则
export function updateBusinessRule(data) {
  return request({
    url: '/redfish/businessRule',
    method: 'put',
    data: data
  })
}

// 删除业务规则
export function delBusinessRule(ruleIds) {
  return request({
    url: '/redfish/businessRule/' + ruleIds,
    method: 'delete'
  })
}

// 获取业务类型列表
export function getBusinessTypes() {
  return request({
    url: '/redfish/businessRule/types/business',
    method: 'get'
  })
}

// 获取硬件类型列表
export function getHardwareTypes() {
  return request({
    url: '/redfish/businessRule/types/hardware',
    method: 'get'
  })
}

// 获取分类硬件类型
export function getHardwareTypesByCategory() {
  return request({
    url: '/redfish/businessRule/types/hardware/categories',
    method: 'get'
  })
}

// 匹配紧急度规则
export function matchUrgencyRule(data) {
  return request({
    url: '/redfish/businessRule/match',
    method: 'post',
    data: data
  })
}

// 获取规则统计信息
export function getBusinessRuleStatistics() {
  return request({
    url: '/redfish/businessRule/statistics',
    method: 'get'
  })
}

// 修改规则状态
export function changeRuleStatus(ruleId, isActive) {
  return request({
    url: '/redfish/businessRule/changeStatus',
    method: 'put',
    params: {
      ruleId,
      isActive
    }
  })
}

// 批量修改规则状态
export function batchChangeRuleStatus(ruleIds, isActive) {
  return request({
    url: '/redfish/businessRule/batchStatus',
    method: 'put',
    params: {
      ruleIds,
      isActive
    }
  })
} 