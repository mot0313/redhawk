<template>
  <div>
    <el-row :gutter="10" class="mb20">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['redfish:urgencyRule:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['redfish:urgencyRule:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['redfish:urgencyRule:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="warning" plain icon="Download" @click="handleExport" v-hasPermi="['redfish:urgencyRule:export']">导出</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="业务类型" prop="businessType">
        <el-select v-model="queryParams.businessType" placeholder="请选择业务类型" clearable style="width: 240px">
          <el-option v-for="item in businessTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="硬件类型" prop="hardwareType">
        <el-select v-model="queryParams.hardwareType" placeholder="请选择硬件类型" clearable style="width: 240px">
          <el-option v-for="item in hardwareTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="紧急程度" prop="urgencyLevel">
        <el-select v-model="queryParams.urgencyLevel" placeholder="请选择紧急程度" clearable style="width: 240px">
          <el-option label="紧急" value="urgent" />
          <el-option label="择期" value="scheduled" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="isActive">
        <el-select v-model="queryParams.isActive" placeholder="规则状态" clearable style="width: 240px">
          <el-option label="启用" :value="1" />
          <el-option label="禁用" :value="0" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>
    <el-table v-loading="loading" :data="urgencyRuleList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="序号" align="center" width="50">
        <template #default="scope">
          {{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}
        </template>
      </el-table-column>
      <el-table-column label="业务类型" align="center" prop="businessType">
        <template #default="scope">
          <span>{{ scope.row.businessTypeName || scope.row.businessType }}</span>
        </template>
      </el-table-column>
      <el-table-column label="硬件类型" align="center" prop="hardwareType">
        <template #default="scope">
          <span>{{ scope.row.hardwareTypeName || scope.row.hardwareType }}</span>
        </template>
      </el-table-column>
      <el-table-column label="紧急程度" align="center" prop="urgencyLevel">
        <template #default="scope">
          <el-tag :type="scope.row.urgencyLevel === 'urgent' ? 'danger' : 'warning'">
            {{ scope.row.urgencyLevel === 'urgent' ? '紧急' : '择期' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="规则描述" align="center" prop="description" show-overflow-tooltip />
      <el-table-column label="是否启用" align="center" prop="isActive">
        <template #default="scope">
          <el-switch
            v-model="scope.row.isActive"
            :active-value="1"
            :inactive-value="0"
            @change="handleStatusChange(scope.row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d} {h}:{i}:{s}') }}</span>
        </template>
      </el-table-column>
              <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="160">
          <template #default="scope">
            <el-tooltip content="详情" placement="top">
              <el-button link type="info" icon="View" @click="handleView(scope.row)" v-hasPermi="['redfish:urgencyRule:query']"></el-button>
            </el-tooltip>
            <el-tooltip content="修改" placement="top">
              <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['redfish:urgencyRule:edit']"></el-button>
            </el-tooltip>
            <el-tooltip content="删除" placement="top">
              <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row, scope.$index)" v-hasPermi="['redfish:urgencyRule:remove']"></el-button>
            </el-tooltip>
          </template>
        </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改紧急度规则对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="urgencyRuleRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="业务类型" prop="businessType">
          <el-select v-model="form.businessType" placeholder="请选择业务类型" style="width: 100%">
            <el-option v-for="item in businessTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="硬件类型" prop="hardwareType">
          <el-select v-model="form.hardwareType" placeholder="请选择硬件类型" style="width: 100%">
            <el-option v-for="item in hardwareTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="紧急程度" prop="urgencyLevel">
          <el-select v-model="form.urgencyLevel" placeholder="请选择紧急程度" style="width: 100%">
            <el-option label="紧急" value="urgent" />
            <el-option label="择期" value="scheduled" />
          </el-select>
        </el-form-item>
        <el-form-item label="规则描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入规则描述" />
        </el-form-item>
        <el-form-item label="是否启用" prop="isActive">
          <el-switch
            v-model="form.isActive"
            :active-value="1"
            :inactive-value="0"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看紧急度规则对话框 -->
    <el-dialog title="紧急度规则详情" v-model="viewOpen" width="700px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="业务类型">
          {{ viewForm.businessType }}
        </el-descriptions-item>
        <el-descriptions-item label="硬件类型">
          {{ viewForm.hardwareType }}
        </el-descriptions-item>
        <el-descriptions-item label="紧急程度">
          <el-tag :type="viewForm.urgencyLevel === 'urgent' ? 'danger' : 'warning'" effect="dark">
            {{ viewForm.urgencyLevel === 'urgent' ? '紧急' : '择期' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="viewForm.isActive === 1 ? 'success' : 'danger'" effect="plain">
            {{ viewForm.isActive === 1 ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ parseTime(viewForm.createTime, '{y}-{m}-{d} {h}:{i}:{s}') }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ parseTime(viewForm.updateTime, '{y}-{m}-{d} {h}:{i}:{s}') }}
        </el-descriptions-item>
        <el-descriptions-item label="规则描述" :span="2">
          {{ viewForm.description || '无' }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="viewOpen = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="UrgencyRule">
import { 
  listUrgencyRule, getUrgencyRule, delUrgencyRule, addUrgencyRule, updateUrgencyRule,
  getBusinessTypeOptions, getHardwareTypeOptions 
} from "@/api/redfish/businessRule";

const { proxy } = getCurrentInstance();

const urgencyRuleList = ref([]);
const businessTypeOptions = ref([]);
const hardwareTypeOptions = ref([]);
const open = ref(false);
const viewOpen = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const data = reactive({
  form: {},
  viewForm: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    businessType: null,
    hardwareType: null,
    urgencyLevel: null,
    isActive: null
  },
  rules: {
    businessType: [
      { required: true, message: "业务类型不能为空", trigger: "change" }
    ],
    hardwareType: [
      { required: true, message: "硬件类型不能为空", trigger: "change" }
    ],
    urgencyLevel: [
      { required: true, message: "紧急程度不能为空", trigger: "change" }
    ],
    isActive: [
      { required: true, message: "状态不能为空", trigger: "change" }
    ]
  }
});

const { queryParams, form, viewForm, rules } = toRefs(data);

  /** 查询紧急度规则列表 */
  function getList() {
    loading.value = true;
    listUrgencyRule(queryParams.value).then(response => {
      urgencyRuleList.value = response.rows;
      total.value = response.total;
      loading.value = false;
    });
  }

/** 获取业务类型选项 */
function getBusinessOptions() {
  getBusinessTypeOptions().then(response => {
    businessTypeOptions.value = response.data;
  });
}

/** 获取硬件类型选项 */
function getHardwareOptions() {
  getHardwareTypeOptions().then(response => {
    hardwareTypeOptions.value = response.data;
  });
}

// 取消按钮
function cancel() {
  open.value = false;
  reset();
}

// 表单重置
function reset() {
  form.value = {
    ruleId: null,
    businessType: null,
    hardwareType: null,
    urgencyLevel: null,
    description: null,
    isActive: 1
  };
  proxy.resetForm("urgencyRuleRef");
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

// 多选框选中数据
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.ruleId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加紧急度规则";
}

/** 查看按钮操作 */
function handleView(row) {
  const _ruleId = row.ruleId;
  getUrgencyRule(_ruleId).then(response => {
    viewForm.value = response.data;
    viewOpen.value = true;
  }).catch(error => {
    console.error('获取紧急度规则详情失败:', error);
    proxy.$modal.msgError('获取紧急度规则详情失败');
  });
}

  /** 修改按钮操作 */
  function handleUpdate(row) {
    reset();
    const _ruleId = row.ruleId || ids.value[0];
    getUrgencyRule(_ruleId).then(response => {
      console.log('获取紧急度规则详情响应:', response);
      form.value = response.data;
      open.value = true;
      title.value = "修改紧急度规则";
    }).catch(error => {
      console.error('获取紧急度规则详情失败:', error);
      proxy.$modal.msgError('获取紧急度规则详情失败');
    });
  }

/** 提交按钮 */
function submitForm() {
  proxy.$refs["urgencyRuleRef"].validate(valid => {
    if (valid) {
      if (form.value.ruleId != null) {
        updateUrgencyRule(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addUrgencyRule(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row, index) {
  const _ruleIds = row.ruleId || ids.value;
  let confirmMessage = '';
  
  if (row.ruleId) {
    // 单个删除
    const rowNumber = (queryParams.value.pageNum - 1) * queryParams.value.pageSize + index + 1;
    confirmMessage = `是否确认删除第${rowNumber}条紧急度规则数据？`;
  } else {
    // 批量删除
    const selectedIndexes = urgencyRuleList.value
      .map((item, idx) => ids.value.includes(item.ruleId) ? (queryParams.value.pageNum - 1) * queryParams.value.pageSize + idx + 1 : null)
      .filter(item => item !== null);
    confirmMessage = `是否确认删除第${selectedIndexes.join('、')}条紧急度规则数据？`;
  }
  
  proxy.$modal.confirm(confirmMessage).then(function() {
    return delUrgencyRule(_ruleIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 导出按钮操作 */
function handleExport() {
  proxy.download("redfish/urgencyRule/export", {
    ...queryParams.value
  }, `urgencyRule_${new Date().getTime()}.xlsx`);
}

/** 状态切换操作 */
function handleStatusChange(row) {
  const statusText = row.isActive === 1 ? '启用' : '禁用';
  const confirmText = `确认要${statusText}该紧急度规则吗？`;
  
  proxy.$modal.confirm(confirmText).then(() => {
    const updateData = {
      ruleId: row.ruleId,
      businessType: row.businessType,
      hardwareType: row.hardwareType,
      urgencyLevel: row.urgencyLevel,
      description: row.description,
      isActive: row.isActive
    };
    
    updateUrgencyRule(updateData).then(response => {
      proxy.$modal.msgSuccess(`${statusText}成功`);
      getList();
    }).catch(() => {
      // 如果更新失败，恢复原状态
      row.isActive = row.isActive === 1 ? 0 : 1;
    });
  }).catch(() => {
    // 如果取消操作，恢复原状态
    row.isActive = row.isActive === 1 ? 0 : 1;
  });
}

onMounted(() => {
  getList();
  getBusinessOptions();
  getHardwareOptions();
});
</script> 