<template>
  <div class="app-container">
    <!-- 搜索条件 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="设备IP" prop="device_ip">
        <el-input
          v-model="queryParams.device_ip"
          placeholder="请输入设备IP"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="日志来源" prop="log_source">
        <el-select v-model="queryParams.log_source" placeholder="请选择日志来源" clearable>
          <el-option label="全部" value="all" />
          <el-option label="系统事件日志(SEL)" value="SEL" />
          <el-option label="管理事件日志(MEL)" value="MEL" />
        </el-select>
      </el-form-item>
      <el-form-item label="严重程度" prop="severity">
        <el-select v-model="queryParams.severity" placeholder="请选择严重程度" clearable>
          <el-option label="全部" value="all" />
          <el-option label="严重" value="CRITICAL" />
          <el-option label="警告" value="WARNING" />
        </el-select>
      </el-form-item>
      <el-form-item label="消息关键词" prop="message_keyword">
        <el-input
          v-model="queryParams.message_keyword"
          placeholder="请输入消息关键词"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="创建时间" style="width: 308px">
        <el-date-picker
          v-model="dateRange"
          value-format="YYYY-MM-DD HH:mm:ss"
          type="datetimerange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :default-time="[new Date(2000, 1, 1, 0, 0, 0), new Date(2000, 1, 1, 23, 59, 59)]"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleCollect"
          v-hasPermi="['redfish:log:collect']"
        >收集日志</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['redfish:log:export']"
        >导出</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          @click="handleCleanup"
          v-hasPermi="['redfish:log:cleanup']"
        >清理日志</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="PieChart"
          @click="showStatistics = true"
        >统计信息</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <!-- 统计信息卡片 -->
    <el-row :gutter="20" class="mb8" v-if="showStatistics">
      <el-col :span="6">
        <el-card class="box-card">
          <div class="card-header">
            <span>总日志数</span>
          </div>
          <div class="card-body">
            <span class="stat-number">{{ statistics.total_count }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="box-card">
          <div class="card-header">
            <span>严重错误</span>
          </div>
          <div class="card-body">
            <span class="stat-number critical">{{ statistics.critical_count }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="box-card">
          <div class="card-header">
            <span>警告</span>
          </div>
          <div class="card-body">
            <span class="stat-number warning">{{ statistics.warning_count }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="box-card">
          <div class="card-header">
            <span>今日日志</span>
          </div>
          <div class="card-body">
            <span class="stat-number">{{ statistics.today_count }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 日志列表 -->
    <el-table v-loading="loading" :data="logList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="设备IP" align="center" prop="device_ip" width="150" />
      <el-table-column label="日志来源" align="center" prop="log_source" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.log_source === 'SEL'" type="primary">SEL</el-tag>
          <el-tag v-else-if="scope.row.log_source === 'MEL'" type="success">MEL</el-tag>
          <el-tag v-else type="info">{{ scope.row.log_source }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="严重程度" align="center" prop="severity" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.severity === 'CRITICAL'" type="danger">严重</el-tag>
          <el-tag v-else-if="scope.row.severity === 'WARNING'" type="warning">警告</el-tag>
          <el-tag v-else type="info">{{ scope.row.severity }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="消息内容" align="center" prop="message" show-overflow-tooltip>
        <template #default="scope">
          <span>{{ scope.row.message || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="传感器类型" align="center" prop="sensor_type" width="120">
        <template #default="scope">
          <span>{{ scope.row.sensor_type || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="created_time" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.created_time, '{y}-{m}-{d} {h}:{i}:{s}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="收集时间" align="center" prop="collected_time" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.collected_time, '{y}-{m}-{d} {h}:{i}:{s}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="180">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleDetail(scope.row)" v-hasPermi="['redfish:log:query']">详情</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['redfish:log:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <pagination
      v-show="total>0"
      :total="total"
      v-model:page="queryParams.page_num"
      v-model:limit="queryParams.page_size"
      @pagination="getList"
    />

    <!-- 收集日志对话框 -->
    <el-dialog :title="collectTitle" v-model="collectOpen" width="500px" append-to-body>
      <el-form :model="collectForm" :rules="collectRules" ref="collectRef" label-width="100px">
        <el-form-item label="设备选择" prop="device_id">
          <el-select v-model="collectForm.device_id" placeholder="请选择设备（留空表示所有设备）" clearable style="width: 100%">
            <el-option
              v-for="device in deviceList"
              :key="device.device_id"
              :label="`${device.hostname} (${device.oob_ip})`"
              :value="device.device_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日志类型" prop="log_type">
          <el-select v-model="collectForm.log_type" placeholder="请选择日志类型" style="width: 100%">
            <el-option label="全部日志" value="all" />
            <el-option label="系统事件日志(SEL)" value="sel" />
            <el-option label="管理事件日志(MEL)" value="mel" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大条目数" prop="max_entries">
          <el-input-number v-model="collectForm.max_entries" :min="1" :max="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="强制刷新" prop="force_refresh">
          <el-switch v-model="collectForm.force_refresh" />
          <span class="ml-2 text-sm text-gray-500">开启后将收集所有日志，否则只收集新增日志</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="collectCancel">取 消</el-button>
          <el-button type="primary" @click="collectSubmit" :loading="collectLoading">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 清理日志对话框 -->
    <el-dialog title="清理日志" v-model="cleanupOpen" width="400px" append-to-body>
      <el-form :model="cleanupForm" :rules="cleanupRules" ref="cleanupRef" label-width="100px">
        <el-form-item label="保留天数" prop="days">
          <el-input-number v-model="cleanupForm.days" :min="1" :max="365" style="width: 100%" />
          <div class="mt-2 text-sm text-gray-500">
            将删除 {{ cleanupForm.days }} 天前的所有日志记录
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cleanupCancel">取 消</el-button>
          <el-button type="danger" @click="cleanupSubmit" :loading="cleanupLoading">确认清理</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 日志详情对话框 -->
    <el-dialog title="日志详情" v-model="detailOpen" width="800px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="日志ID">{{ logDetail.log_id }}</el-descriptions-item>
        <el-descriptions-item label="设备ID">{{ logDetail.device_id }}</el-descriptions-item>
        <el-descriptions-item label="设备IP">{{ logDetail.device_ip }}</el-descriptions-item>
        <el-descriptions-item label="日志来源">{{ logDetail.log_source }}</el-descriptions-item>
        <el-descriptions-item label="严重程度">
          <el-tag v-if="logDetail.severity === 'CRITICAL'" type="danger">严重</el-tag>
          <el-tag v-else-if="logDetail.severity === 'WARNING'" type="warning">警告</el-tag>
          <el-tag v-else type="info">{{ logDetail.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="条目类型">{{ logDetail.entry_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="消息ID">{{ logDetail.message_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="传感器类型">{{ logDetail.sensor_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="传感器编号">{{ logDetail.sensor_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(logDetail.created_time) }}</el-descriptions-item>
        <el-descriptions-item label="收集时间">{{ parseTime(logDetail.collected_time) }}</el-descriptions-item>
        <el-descriptions-item label="创建者">{{ logDetail.create_by || '-' }}</el-descriptions-item>
        <el-descriptions-item label="消息内容" span="2">
          <div style="max-height: 200px; overflow-y: auto;">
            {{ logDetail.message || '-' }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="备注" span="2">{{ logDetail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup name="RedfishLog">
import { 
  listRedfishLog, 
  getRedfishLog, 
  getRedfishLogStatistics,
  collectDeviceLogs,
  cleanupOldLogs,
  delRedfishLog,
  exportLogsData,
  getDeviceSelectList
} from "@/api/redfish/log";
import { parseTime } from "@/utils/ruoyi";

const { proxy } = getCurrentInstance();

const logList = ref([]);
const detailOpen = ref(false);
const collectOpen = ref(false);
const cleanupOpen = ref(false);
const loading = ref(true);
const collectLoading = ref(false);
const cleanupLoading = ref(false);
const showSearch = ref(true);
const showStatistics = ref(false);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const collectTitle = ref("");
const dateRange = ref([]);
const deviceList = ref([]);

// 统计信息
const statistics = ref({
  total_count: 0,
  critical_count: 0,
  warning_count: 0,
  sel_count: 0,
  mel_count: 0,
  today_count: 0,
  recent_7days_count: 0
});

// 查询参数
const queryParams = ref({
  page_num: 1,
  page_size: 10,
  device_ip: null,
  log_source: null,
  severity: null,
  message_keyword: null,
  start_time: null,
  end_time: null
});

// 收集表单
const collectForm = ref({
  device_id: null,
  log_type: "all",
  max_entries: 100,
  force_refresh: false
});

// 清理表单
const cleanupForm = ref({
  days: 30
});

// 日志详情
const logDetail = ref({});

// 表单校验
const collectRules = {
  log_type: [
    { required: true, message: "日志类型不能为空", trigger: "change" }
  ],
  max_entries: [
    { required: true, message: "最大条目数不能为空", trigger: "blur" }
  ]
};

const cleanupRules = {
  days: [
    { required: true, message: "保留天数不能为空", trigger: "blur" }
  ]
};

/** 查询日志列表 */
function getList() {
  loading.value = true;
  queryParams.value.start_time = dateRange.value ? dateRange.value[0] : null;
  queryParams.value.end_time = dateRange.value ? dateRange.value[1] : null;
  
  listRedfishLog(queryParams.value).then(response => {
    logList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

/** 获取统计信息 */
function getStatistics() {
  getRedfishLogStatistics().then(response => {
    statistics.value = response.data;
  });
}

/** 获取设备列表 */
function getDeviceList() {
  getDeviceSelectList().then(response => {
    deviceList.value = response.rows || [];
  });
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.page_num = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  dateRange.value = [];
  proxy.resetForm("queryRef");
  handleQuery();
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.log_id);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 详情按钮操作 */
function handleDetail(row) {
  const logId = row.log_id;
  getRedfishLog(logId).then(response => {
    logDetail.value = response.data;
    detailOpen.value = true;
  });
}

/** 收集日志按钮操作 */
function handleCollect() {
  reset();
  getDeviceList();
  collectOpen.value = true;
  collectTitle.value = "收集设备日志";
}

/** 清理日志按钮操作 */
function handleCleanup() {
  cleanupForm.value = {
    days: 30
  };
  cleanupOpen.value = true;
}

/** 删除按钮操作 */
function handleDelete(row) {
  const logIds = row.log_id || ids.value;
  proxy.$modal.confirm('是否确认删除选中的日志记录？').then(function() {
    return delRedfishLog(logIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 导出按钮操作 */
function handleExport() {
  proxy.download('redfish/log/export/data', {
    ...queryParams.value
  }, `redfish_logs_${new Date().getTime()}.xlsx`);
}

/** 表单重置 */
function reset() {
  collectForm.value = {
    device_id: null,
    log_type: "all",
    max_entries: 100,
    force_refresh: false
  };
  proxy.resetForm("collectRef");
}

/** 取消收集 */
function collectCancel() {
  collectOpen.value = false;
  reset();
}

/** 提交收集 */
function collectSubmit() {
  proxy.$refs["collectRef"].validate(valid => {
    if (valid) {
      collectLoading.value = true;
      collectDeviceLogs(collectForm.value).then(response => {
        proxy.$modal.msgSuccess(response.data.message);
        collectOpen.value = false;
        getList();
        getStatistics();
      }).finally(() => {
        collectLoading.value = false;
      });
    }
  });
}

/** 取消清理 */
function cleanupCancel() {
  cleanupOpen.value = false;
}

/** 提交清理 */
function cleanupSubmit() {
  proxy.$refs["cleanupRef"].validate(valid => {
    if (valid) {
      proxy.$modal.confirm(`确认清理 ${cleanupForm.value.days} 天前的所有日志记录？此操作不可恢复。`).then(() => {
        cleanupLoading.value = true;
        cleanupOldLogs(cleanupForm.value.days).then(response => {
          proxy.$modal.msgSuccess(response.data.message);
          cleanupOpen.value = false;
          getList();
          getStatistics();
        }).finally(() => {
          cleanupLoading.value = false;
        });
      });
    }
  });
}

onMounted(() => {
  getList();
  getStatistics();
});
</script>

<style scoped>
.box-card {
  margin-bottom: 10px;
}

.card-header {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.card-body {
  text-align: center;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.stat-number.critical {
  color: #F56C6C;
}

.stat-number.warning {
  color: #E6A23C;
}

.ml-2 {
  margin-left: 8px;
}

.text-sm {
  font-size: 12px;
}

.text-gray-500 {
  color: #9CA3AF;
}

.mt-2 {
  margin-top: 8px;
}
</style>
