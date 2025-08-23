<template>
  <div class="app-container">
    <!-- 设备选择区域 -->
    <el-card class="mb-4">
      <template #header>
        <div class="card-header">
          <span>🔍 设备选择</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="选择设备">
            <el-select 
              v-model="selectedDeviceId" 
              placeholder="请选择要查看日志的设备" 
              clearable 
              filterable
              style="width: 100%"
              @change="handleDeviceChange"
            >
              <el-option
                v-for="device in deviceList"
                :key="device.deviceId"
                :label="`${device.hostname} (${device.oobIp})`"
                :value="device.deviceId"
              >
                <span style="float: left">{{ device.hostname }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">{{ device.oobIp }}</span>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="6">
          <el-form-item label="日志类型">
            <el-select v-model="collectForm.logType" style="width: 100%">
              <el-option label="全部日志" value="all" />
              <el-option label="系统事件日志(SEL)" value="sel" />
              <el-option label="管理事件日志(MEL)" value="mel" />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="6">
          <el-form-item label="最大条目数">
            <el-input-number 
              v-model="collectForm.maxEntries" 
              :min="1" 
              :max="1000" 
              style="width: 100%" 
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="4">
          <el-form-item label=" ">
            <el-button 
              type="primary" 
              :loading="collecting"
              :disabled="!selectedDeviceId"
              @click="collectLogs"
              style="width: 100%"
              v-hasPermi="['redfish:log:temp:collect']"
            >
              <i class="fa fa-search"></i> 收集日志
            </el-button>
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 设备信息显示 -->
    <el-card v-if="deviceInfo.deviceId" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>📋 设备信息</span>
        </div>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="设备名称">{{ deviceInfo.deviceName }}</el-descriptions-item>
        <el-descriptions-item label="设备IP">{{ deviceInfo.deviceIp }}</el-descriptions-item>
        <el-descriptions-item label="收集时间">{{ formatTime(collectTime) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 统计信息 -->
    <el-card v-if="statistics.totalCollected > 0" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>📊 收集统计</span>
          <div style="float: right">
            <el-button size="small" @click="clearLogs">清空日志</el-button>
            <el-button 
              size="small" 
              type="success" 
              @click="exportLogs"
              v-hasPermi="['redfish:log:temp:export']"
            >导出日志</el-button>
          </div>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-number">{{ statistics.totalCollected }}</div>
            <div class="stat-label">总日志数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-number critical">{{ statistics.criticalCount }}</div>
            <div class="stat-label">严重错误</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-number warning">{{ statistics.warningCount }}</div>
            <div class="stat-label">警告信息</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-number">{{ filteredLogs.length }}</div>
            <div class="stat-label">显示条目</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 日志筛选工具栏 -->
    <el-card v-if="logsList.length > 0" class="mb-4">
      <!-- 快速筛选标签 -->
      <div class="quick-filters mb-3">
        <span class="filter-label">快速筛选：</span>
        <el-tag 
          :type="filterSeverity === '' ? 'primary' : ''"
          @click="quickFilterSeverity('')"
          class="filter-tag"
        >全部 ({{ logsList.length }})</el-tag>
        <el-tag 
          :type="filterSeverity === 'CRITICAL' ? 'danger' : ''"
          @click="quickFilterSeverity('CRITICAL')"
          class="filter-tag"
        >严重 ({{ statistics.criticalCount }})</el-tag>
        <el-tag 
          :type="filterSeverity === 'WARNING' ? 'warning' : ''"
          @click="quickFilterSeverity('WARNING')"
          class="filter-tag"
        >警告 ({{ statistics.warningCount }})</el-tag>
      </div>
      
      <!-- 详细筛选 -->
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="filterKeyword"
            placeholder="搜索日志内容..."
            clearable
            @input="filterLogs"
          >
            <template #prefix>
              <i class="fa fa-search"></i>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterSeverity" placeholder="筛选级别" clearable @change="filterLogs">
            <el-option label="全部级别" value="" />
            <el-option label="严重错误" value="CRITICAL" />
            <el-option label="警告信息" value="WARNING" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterSource" placeholder="筛选来源" clearable @change="filterLogs">
            <el-option label="全部来源" value="" />
            <el-option label="SEL" value="SEL" />
            <el-option label="MEL" value="MEL" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="filterTimeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="filterLogs"
            style="width: 100%"
          />
        </el-col>
        <el-col :span="4">
          <el-button @click="resetFilters">重置筛选</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 日志列表 -->
    <el-card v-if="logsList.length > 0">
      <template #header>
        <div class="card-header">
          <span>📄 日志列表 ({{ filteredLogs.length }} / {{ logsList.length }} 条)</span>
        </div>
      </template>
      
      <el-table 
        :data="filteredLogs" 
        stripe 
        style="width: 100%" 
        max-height="500"
        v-loading="collecting"
      >
        <el-table-column prop="logSource" label="来源" width="80" align="center" />
        <el-table-column prop="severity" label="级别" width="100" align="center">
          <template #default="scope">
            <el-tag 
              v-if="scope.row.severity === 'CRITICAL'" 
              type="danger" 
              size="small"
            >严重</el-tag>
            <el-tag 
              v-else-if="scope.row.severity === 'WARNING'" 
              type="warning" 
              size="small"
            >警告</el-tag>
            <el-tag 
              v-else 
              type="info" 
              size="small"
            >{{ scope.row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdTime" label="创建时间" width="160" align="center">
          <template #default="scope">
            <span>{{ formatCreatedTime(scope.row.createdTime) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="message" label="消息内容" show-overflow-tooltip />
        <el-table-column label="操作" width="100" align="center">
          <template #default="scope">
            <el-button type="text" size="small" @click="viewLogDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 空状态 -->
    <el-empty 
      v-if="!collecting && logsList.length === 0 && selectedDeviceId"
      description="暂无日志数据"
      :image-size="100"
    >
      <el-button type="primary" @click="collectLogs">重新收集</el-button>
    </el-empty>

    <el-empty 
      v-if="!selectedDeviceId && deviceList.length > 0"
      description="请选择设备开始查看日志"
      :image-size="100"
    />
    
    <el-empty 
      v-if="deviceList.length === 0"
      description="无法获取设备列表，请检查权限配置"
      :image-size="100"
    >
      <el-button type="primary" @click="getDeviceList">重新获取</el-button>
    </el-empty>

    <!-- 日志详情对话框 -->
    <el-dialog title="日志详情" v-model="detailDialogVisible" width="800px">
      <el-descriptions :column="2" border v-if="selectedLog">
        <el-descriptions-item label="主机名">{{ deviceInfo.deviceName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ selectedLog.logSource }}</el-descriptions-item>
        <el-descriptions-item label="级别">
          <el-tag 
            v-if="selectedLog.severity === 'CRITICAL'" 
            type="danger"
          >严重</el-tag>
          <el-tag 
            v-else-if="selectedLog.severity === 'WARNING'" 
            type="warning"
          >警告</el-tag>
          <el-tag v-else type="info">{{ selectedLog.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatCreatedTime(selectedLog.createdTime) }}</el-descriptions-item>
        <el-descriptions-item label="条目类型">{{ selectedLog.entryType || '-' }}</el-descriptions-item>
        <el-descriptions-item label="条目ID">{{ selectedLog.entryId || '-' }}</el-descriptions-item>
        <el-descriptions-item label="消息内容" span="2">
          <div style="max-height: 200px; overflow-y: auto; word-break: break-all;">
            {{ selectedLog.message || '-' }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="原始日志数据" span="2">
          <div v-if="selectedLog.originalData" 
               style="max-height: 300px; overflow-y: auto; word-break: break-all; background: #f5f7fa; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 11px; white-space: pre-wrap;">
            {{ selectedLog.originalData }}
          </div>
          <div v-else>暂无原始日志数据</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup name="TempLogView">
import { ref, reactive, onMounted, computed, getCurrentInstance } from 'vue';
import { collectDeviceLogs, getDeviceListForLog } from "@/api/redfish/log";
import { parseTime } from "@/utils/ruoyi";

const { proxy } = getCurrentInstance();

// 响应式数据
const selectedDeviceId = ref(null);
const collecting = ref(false);
const deviceList = ref([]);
const logsList = ref([]);
const filteredLogs = ref([]);
const detailDialogVisible = ref(false);
const selectedLog = ref(null);
const collectTime = ref(null);

// 收集表单
const collectForm = reactive({
  logType: "all",
  maxEntries: 100
});

// 设备信息
const deviceInfo = reactive({
  deviceId: null,
  deviceIp: '',
  deviceName: ''
});

// 统计信息
const statistics = reactive({
  totalCollected: 0,
  criticalCount: 0,
  warningCount: 0
});

// 筛选条件
const filterKeyword = ref('');
const filterSeverity = ref('');
const filterSource = ref('');
const filterTimeRange = ref([]);

/** 检查时间是否有效 */
function isValidTime(timeStr) {
  if (!timeStr) return false;
  
  // 检查特殊的无效时间标识
  const invalidPatterns = [
    '1900-01-01',
    '0000-00-00',
    '1970-01-01'
  ];
  
  for (const pattern of invalidPatterns) {
    if (timeStr.startsWith(pattern)) {
      return false;
    }
  }
  
  return true;
}

/** 格式化创建时间显示 */
function formatCreatedTime(timeStr) {
  if (!timeStr || !isValidTime(timeStr)) {
    return '未知时间';
  }
  return parseTime(timeStr, '{y}-{m}-{d} {h}:{i}:{s}');
}

/** 格式化时间 */
function formatTime(time) {
  if (!time) return '-';
  return parseTime(time, '{y}-{m}-{d} {h}:{i}:{s}');
}

/** 获取设备列表 */
async function getDeviceList() {
  try {
    const response = await getDeviceListForLog();
    deviceList.value = response.data.rows || [];
  } catch (error) {
    console.error('获取设备列表失败:', error);
    proxy.$modal.msgError('获取设备列表失败，请确保拥有日志查看权限');
    // 如果获取失败，显示友好提示
    deviceList.value = [];
  }
}

/** 设备选择变化 */
function handleDeviceChange() {
  // 清空之前的数据
  clearLogs();
}

/** 收集日志 */
async function collectLogs() {
  if (!selectedDeviceId.value) {
    proxy.$modal.msgWarning('请先选择设备');
    return;
  }

  collecting.value = true;
  
  try {
    const params = {
      deviceId: selectedDeviceId.value,
      logType: collectForm.logType,
      maxEntries: collectForm.maxEntries,
      forceRefresh: true,
      noStorage: true  // 临时查看页面始终不保存
    };

    const response = await collectDeviceLogs(params);
    
    if (response.data.success) {
      // 更新设备信息
      deviceInfo.deviceId = response.data.deviceId;
      deviceInfo.deviceIp = response.data.deviceIp;
      deviceInfo.deviceName = response.data.deviceName;
      
      // 更新统计信息
      statistics.totalCollected = response.data.totalCollected;
      statistics.criticalCount = response.data.criticalCount;
      statistics.warningCount = response.data.warningCount;
      
      // 更新日志列表
      logsList.value = response.data.logsData || [];
      collectTime.value = new Date();
      
      // 应用筛选
      filterLogs();
      
      proxy.$modal.msgSuccess(response.data.message);
    } else {
      proxy.$modal.msgError(response.data.message || '收集日志失败');
    }
  } catch (error) {
    proxy.$modal.msgError('收集日志时发生错误');
  } finally {
    collecting.value = false;
  }
}

/** 筛选日志 */
function filterLogs() {
  let filtered = [...logsList.value];
  
  // 关键词筛选
  if (filterKeyword.value) {
    const keyword = filterKeyword.value.toLowerCase();
    filtered = filtered.filter(log => 
      (log.message || '').toLowerCase().includes(keyword)
    );
  }
  
  // 级别筛选
  if (filterSeverity.value) {
    filtered = filtered.filter(log => log.severity === filterSeverity.value);
  }
  
  // 来源筛选
  if (filterSource.value) {
    filtered = filtered.filter(log => log.logSource === filterSource.value);
  }
  
  // 时间范围筛选
  if (filterTimeRange.value && filterTimeRange.value.length === 2) {
    const [startTime, endTime] = filterTimeRange.value;
    filtered = filtered.filter(log => {
      const logTime = new Date(log.createdTime);
      return logTime >= new Date(startTime) && logTime <= new Date(endTime);
    });
  }
  
  filteredLogs.value = filtered;
}

/** 重置筛选 */
function resetFilters() {
  filterKeyword.value = '';
  filterSeverity.value = '';
  filterSource.value = '';
  filterTimeRange.value = [];
  filterLogs();
}

/** 快速筛选级别 */
function quickFilterSeverity(severity) {
  filterSeverity.value = severity;
  filterLogs();
}

/** 清空日志 */
function clearLogs() {
  logsList.value = [];
  filteredLogs.value = [];
  collectTime.value = null;
  
  // 重置统计信息
  statistics.totalCollected = 0;
  statistics.criticalCount = 0;
  statistics.warningCount = 0;
  
  // 重置设备信息
  deviceInfo.deviceId = null;
  deviceInfo.deviceIp = '';
  deviceInfo.deviceName = '';
  
  // 重置筛选
  resetFilters();
}

/** 导出日志 */
function exportLogs() {
  if (filteredLogs.value.length === 0) {
    proxy.$modal.msgWarning('没有可导出的日志数据');
    return;
  }
  
  // 这里可以实现导出功能
  proxy.$modal.msgInfo('导出功能开发中...');
}

/** 查看日志详情 */
function viewLogDetail(log) {
  selectedLog.value = log;
  detailDialogVisible.value = true;
}

/** 初始化 */
onMounted(() => {
  getDeviceList();
});
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 16px;
}

.card-header {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-number.critical {
  color: #F56C6C;
}

.stat-number.warning {
  color: #E6A23C;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.el-form-item {
  margin-bottom: 0;
}

/* 快速筛选样式 */
.quick-filters {
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
}

.filter-tag {
  margin-right: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.mb-3 {
  margin-bottom: 12px;
}
</style>
