/**
 * 通知公告本地存储管理工具
 * 用于跟踪用户的已读通知状态，实现未读提示功能
 */

// 获取当前用户的存储key
function getUserStorageKey() {
  // 从localStorage获取当前用户信息
  try {
    const userInfo = localStorage.getItem('user-info')
    if (userInfo) {
      const user = JSON.parse(userInfo)
      const userId = user?.user?.userId || user?.userId
      if (userId) {
        return `notice_read_list_${userId}`
      }
    }
  } catch (error) {
    console.warn('获取用户信息失败:', error)
  }
  
  // 兜底方案：使用通用key（向后兼容）
  return 'notice_read_list'
}

/**
 * 获取已读通知ID列表
 * @returns {Array<number>} 已读通知ID数组
 */
export function getReadNoticeIds() {
  try {
    const storageKey = getUserStorageKey()
    const stored = localStorage.getItem(storageKey)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.warn('获取已读通知列表失败:', error)
    return []
  }
}

/**
 * 标记通知为已读
 * @param {number} noticeId 通知ID
 */
export function markNoticeAsRead(noticeId) {
  try {
    const readIds = getReadNoticeIds()
    if (!readIds.includes(noticeId)) {
      readIds.push(noticeId)
      const storageKey = getUserStorageKey()
      localStorage.setItem(storageKey, JSON.stringify(readIds))
    }
  } catch (error) {
    console.warn('标记通知已读失败:', error)
  }
}

/**
 * 批量标记通知为已读
 * @param {Array<number>} noticeIds 通知ID数组
 */
export function markNoticesAsRead(noticeIds) {
  try {
    const readIds = getReadNoticeIds()
    const newReadIds = [...new Set([...readIds, ...noticeIds])]
    const storageKey = getUserStorageKey()
    localStorage.setItem(storageKey, JSON.stringify(newReadIds))
  } catch (error) {
    console.warn('批量标记通知已读失败:', error)
  }
}

/**
 * 检查通知是否已读
 * @param {number} noticeId 通知ID
 * @returns {boolean} 是否已读
 */
export function isNoticeRead(noticeId) {
  const readIds = getReadNoticeIds()
  return readIds.includes(noticeId)
}

/**
 * 计算未读通知数量
 * @param {Array} notices 通知列表
 * @returns {number} 未读数量
 */
export function getUnreadCount(notices) {
  if (!Array.isArray(notices)) {
    return 0
  }
  
  const readIds = getReadNoticeIds()
  return notices.filter(notice => !readIds.includes(notice.noticeId)).length
}

/**
 * 获取未读通知列表
 * @param {Array} notices 通知列表
 * @returns {Array} 未读通知列表
 */
export function getUnreadNotices(notices) {
  if (!Array.isArray(notices)) {
    return []
  }
  
  const readIds = getReadNoticeIds()
  return notices.filter(notice => !readIds.includes(notice.noticeId))
}

/**
 * 清空所有已读记录（可用于测试或重置）
 */
export function clearReadHistory() {
  try {
    const storageKey = getUserStorageKey()
    localStorage.removeItem(storageKey)
  } catch (error) {
    console.warn('清空已读历史失败:', error)
  }
}

/**
 * 清理过期的已读记录（移除超过30天的记录）
 * 注意：这个函数需要配合服务器时间戳使用
 * @param {Array} currentNoticeIds 当前有效的通知ID列表
 */
export function cleanupExpiredReads(currentNoticeIds) {
  try {
    const readIds = getReadNoticeIds()
    const validReadIds = readIds.filter(id => currentNoticeIds.includes(id))
    const storageKey = getUserStorageKey()
    localStorage.setItem(storageKey, JSON.stringify(validReadIds))
  } catch (error) {
    console.warn('清理过期已读记录失败:', error)
  }
}

// 默认导出所有函数
export default {
  getReadNoticeIds,
  markNoticeAsRead,
  markNoticesAsRead,
  isNoticeRead,
  getUnreadCount,
  getUnreadNotices,
  clearReadHistory,
  cleanupExpiredReads
}
