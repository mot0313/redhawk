// 深度调试parseTime函数
function parseTimeDebug(time, pattern) {
  console.log('=== parseTime Debug ===')
  console.log('1. 输入:', time)
  
  if (!time) {
    console.log('2. 时间为空，返回null')
    return null
  }
  
  const format = pattern || '{y}-{m}-{d} {h}:{i}:{s}'
  console.log('3. 格式:', format)
  
  let date
  if (typeof time === 'object') {
    date = time
    console.log('4. 时间是对象类型')
  } else {
    console.log('5. 时间是字符串，开始处理...')
    if ((typeof time === 'string') && (/^[0-9]+$/.test(time))) {
      time = parseInt(time)
      console.log('6a. 转换为数字:', time)
    } else if (typeof time === 'string') {
      console.log('6b. 字符串处理前:', time)
      time = time.replace(new RegExp(/-/gm), '/').replace('T', ' ').replace(new RegExp(/\.[\d]{3}/gm), '').replace(/Z$/gm, '');
      console.log('6c. 字符串处理后:', time)
    }
    if ((typeof time === 'number') && (time.toString().length === 10)) {
      time = time * 1000
      console.log('7. 时间戳转换:', time)
    }
    date = new Date(time)
    console.log('8. Date对象:', date)
    console.log('9. Date是否有效:', !isNaN(date.getTime()))
  }
  
  const formatObj = {
    y: date.getFullYear(),
    m: date.getMonth() + 1,
    d: date.getDate(),
    h: date.getHours(),
    i: date.getMinutes(),
    s: date.getSeconds()
  }
  console.log('10. 格式化对象:', formatObj)
  
  const time_str = format.replace(/{(y|m|d|h|i|s|a)+}/g, (result, key) => {
    let value = formatObj[key]
    console.log(`11. 替换 ${key}: ${value} -> ${value || 0}`)
    if (result.length > 0 && value < 10) {
      value = '0' + value
    }
    return value || 0
  })
  
  console.log('12. 最终结果:', time_str)
  return time_str
}

// 测试真实的ISO时间
const testTime = '2025-08-21T12:22:02.194Z'
parseTimeDebug(testTime, '{y}-{m}-{d} {h}:{i}:{s}')

console.log('\n=== 测试无效时间 ===')
parseTimeDebug('invalid-time', '{y}-{m}-{d} {h}:{i}:{s}')
