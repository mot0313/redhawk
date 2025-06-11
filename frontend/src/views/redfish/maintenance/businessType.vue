<template>
    <div>
      <el-row :gutter="10" class="mb20">
        <el-col :span="1.5">
          <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['redfish:businessType:add']">新增</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="success"
            plain
            icon="Edit"
            :disabled="single"
            @click="handleUpdate"
            v-hasPermi="['redfish:businessType:edit']"
          >修改</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="danger"
            plain
            icon="Delete"
            :disabled="multiple"
            @click="handleDelete"
            v-hasPermi="['redfish:businessType:remove']"
          >删除</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button type="warning" plain icon="Download" @click="handleExport" v-hasPermi="['redfish:businessType:export']">导出</el-button>
        </el-col>
        <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
      </el-row>
      <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
        <el-form-item label="类型编码" prop="typeCode">
          <el-input
            v-model="queryParams.typeCode"
            placeholder="请输入类型编码"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="类型名称" prop="typeName">
          <el-input
            v-model="queryParams.typeName"
            placeholder="请输入类型名称"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="状态" prop="isActive">
          <el-select v-model="queryParams.isActive" placeholder="业务类型状态" clearable style="width: 240px">
            <el-option v-for="dict in sys_normal_disable" :key="dict.value" :label="dict.label" :value="dict.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table v-loading="loading" :data="businessTypeList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="序号" align="center" width="50">
          <template #default="scope">
            {{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column label="类型编码" align="center" prop="typeCode" />
        <el-table-column label="类型名称" align="center" prop="typeName" />
        <el-table-column label="类型描述" align="center" prop="typeDescription" show-overflow-tooltip />
        <el-table-column label="排序" align="center" prop="sortOrder" />
        <el-table-column label="状态" align="center" prop="isActive">
          <template #default="scope">
            <dict-tag :options="sys_normal_disable" :value="scope.row.isActive" />
          </template>
        </el-table-column>
        <el-table-column label="创建时间" align="center" prop="createTime" width="180">
          <template #default="scope">
            <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d} {h}:{i}:{s}') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="160">
          <template #default="scope">
            <el-button link type="info" icon="View" @click="handleView(scope.row)" v-hasPermi="['redfish:businessType:query']"></el-button>
            <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['redfish:businessType:edit']"></el-button>
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row, scope.$index)" v-hasPermi="['redfish:businessType:remove']"></el-button>
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
  
      <!-- 添加或修改业务类型对话框 -->
      <el-dialog :title="title" v-model="open" width="500px" append-to-body>
        <el-form ref="businessTypeRef" :model="form" :rules="rules" label-width="80px">
          <el-form-item label="类型编码" prop="typeCode">
            <el-input v-model="form.typeCode" placeholder="请输入类型编码" />
          </el-form-item>
          <el-form-item label="类型名称" prop="typeName">
            <el-input v-model="form.typeName" placeholder="请输入类型名称" />
          </el-form-item>
          <el-form-item label="类型描述" prop="typeDescription">
            <el-input v-model="form.typeDescription" type="textarea" placeholder="请输入类型描述" />
          </el-form-item>
          <el-form-item label="排序" prop="sortOrder">
            <el-input-number v-model="form.sortOrder" controls-position="right" :min="0" />
          </el-form-item>
          <el-form-item label="状态" prop="isActive">
            <el-radio-group v-model="form.isActive">
              <el-radio v-for="dict in sys_normal_disable" :key="dict.value" :value="parseInt(dict.value)">{{ dict.label }}</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button type="primary" @click="submitForm">确 定</el-button>
            <el-button @click="cancel">取 消</el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 查看业务类型对话框 -->
      <el-dialog title="业务类型详情" v-model="viewOpen" width="700px" append-to-body>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="类型编码">
            {{ viewForm.typeCode }}
          </el-descriptions-item>
          <el-descriptions-item label="类型名称">
            {{ viewForm.typeName }}
          </el-descriptions-item>
          <el-descriptions-item label="排序">
            {{ viewForm.sortOrder }}
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
          <el-descriptions-item label="类型描述" :span="2">
            {{ viewForm.typeDescription || '无' }}
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
  
  <script setup name="BusinessType">
  import { listBusinessType, getBusinessType, delBusinessType, addBusinessType, updateBusinessType } from "@/api/redfish/businessRule";
  
  const { proxy } = getCurrentInstance();
  const { sys_normal_disable } = proxy.useDict("sys_normal_disable");
  
  const businessTypeList = ref([]);
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
      typeCode: null,
      typeName: null,
      isActive: null
    },
    rules: {
      typeCode: [
        { required: true, message: "类型编码不能为空", trigger: "blur" }
      ],
      typeName: [
        { required: true, message: "类型名称不能为空", trigger: "blur" }
      ],
      sortOrder: [
        { required: true, message: "排序不能为空", trigger: "blur" }
      ],
      isActive: [
        { required: true, message: "状态不能为空", trigger: "change" }
      ]
    }
  });
  
  const { queryParams, form, viewForm, rules } = toRefs(data);
  
  /** 查询业务类型列表 */
  function getList() {
    loading.value = true;
    listBusinessType(queryParams.value).then(response => {
      businessTypeList.value = response.rows;
      total.value = response.total;
      loading.value = false;
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
      typeId: null,
      typeCode: null,
      typeName: null,
      typeDescription: null,
      sortOrder: 0,
      isActive: 1
    };
    proxy.resetForm("businessTypeRef");
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
    ids.value = selection.map(item => item.typeId);
    single.value = selection.length != 1;
    multiple.value = !selection.length;
  }
  
  /** 新增按钮操作 */
  function handleAdd() {
    reset();
    open.value = true;
    title.value = "添加业务类型";
  }

  /** 查看按钮操作 */
  function handleView(row) {
    const _typeId = row.typeId;
    getBusinessType(_typeId).then(response => {
      viewForm.value = response.data;
      viewOpen.value = true;
    }).catch(error => {
      console.error('获取业务类型详情失败:', error);
      proxy.$modal.msgError('获取业务类型详情失败');
    });
  }
  
  /** 修改按钮操作 */
  function handleUpdate(row) {
    reset();
    const _typeId = row.typeId || ids.value[0];
    getBusinessType(_typeId).then(response => {
      console.log('获取业务类型详情响应:', response);
      form.value = response.data;
      open.value = true;
      title.value = "修改业务类型";
    }).catch(error => {
      console.error('获取业务类型详情失败:', error);
      proxy.$modal.msgError('获取业务类型详情失败');
    });
  }
  
  /** 提交按钮 */
  function submitForm() {
    proxy.$refs["businessTypeRef"].validate(valid => {
      if (valid) {
        if (form.value.typeId != null) {
          updateBusinessType(form.value).then(response => {
            proxy.$modal.msgSuccess("修改成功");
            open.value = false;
            getList();
          });
        } else {
          addBusinessType(form.value).then(response => {
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
    const _typeIds = row.typeId || ids.value;
    let confirmMessage = '';
    
    if (row.typeId) {
      // 单个删除
      const rowNumber = (queryParams.value.pageNum - 1) * queryParams.value.pageSize + index + 1;
      confirmMessage = `是否确认删除第${rowNumber}条业务类型数据？`;
    } else {
      // 批量删除
      const selectedIndexes = businessTypeList.value
        .map((item, idx) => ids.value.includes(item.typeId) ? (queryParams.value.pageNum - 1) * queryParams.value.pageSize + idx + 1 : null)
        .filter(item => item !== null);
      confirmMessage = `是否确认删除第${selectedIndexes.join('、')}条业务类型数据？`;
    }
    
    proxy.$modal.confirm(confirmMessage).then(function() {
      return delBusinessType(_typeIds);
    }).then(() => {
      getList();
      proxy.$modal.msgSuccess("删除成功");
    }).catch(() => {});
  }
  
  /** 导出按钮操作 */
  function handleExport() {
    proxy.download("redfish/businessType/export", {
      ...queryParams.value
    }, `businessType_${new Date().getTime()}.xlsx`);
  }
  
  onMounted(() => {
    getList();
  });
  </script>