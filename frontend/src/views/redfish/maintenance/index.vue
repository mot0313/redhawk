<template>
  <div class="app-container">
    <!-- Tab 切换 -->
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">

      <!-- 紧急度规则管理 -->
      <el-tab-pane label="紧急度规则" name="urgencyRule">
        <urgency-rule v-if="activeTab === 'urgencyRule'" />
      </el-tab-pane>

      <!-- 业务类型管理 -->
      <el-tab-pane label="业务类型管理" name="businessType">
        <business-type v-if="activeTab === 'businessType'" />
      </el-tab-pane>
      
      <!-- 硬件类型管理 -->
      <el-tab-pane label="硬件类型管理" name="hardwareType">
        <hardware-type v-if="activeTab === 'hardwareType'" />
      </el-tab-pane>
      

    </el-tabs>
  </div>
</template>

<script setup name="MaintenanceSchedule">
import BusinessType from './businessType.vue';
import HardwareType from './hardwareType.vue';
import UrgencyRule from './urgencyRule.vue';

// Tab切换状态，默认激活业务类型管理
const activeTab = ref('urgencyRule');

/** Tab切换处理 */
function handleTabClick(tab) {
  activeTab.value = tab.name;
}

onMounted(() => {
  // 组件挂载时无需额外操作
});
</script>

<style scoped>
/* 保留必要的样式 */
</style> 