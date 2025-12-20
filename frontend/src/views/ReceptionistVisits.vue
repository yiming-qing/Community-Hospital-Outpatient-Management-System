<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, FirstAidKit, Money, Wallet, CreditCard } from '@element-plus/icons-vue'

import { listVisits, payVisit, updateVisitStatus } from '../api/receptionist'

const loading = ref(false)
const visits = ref([])
const statusFilter = ref('')

const payDialogVisible = ref(false)
const payDialogLoading = ref(false)
const selected = ref(null)

const payForm = reactive({
  total_amount: 0,
  insurance_amount: 0,
  self_pay_amount: null,
})

async function load() {
  loading.value = true
  try {
    visits.value = await listVisits({ status: statusFilter.value || undefined })
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function toStatus(row, status) {
  try {
    await updateVisitStatus(row.visit_id, status)
    ElMessage.success('已更新')
    await load()
  } catch (e) {
    ElMessage.error(e?.message || '更新失败')
  }
}

function openPay(row) {
  selected.value = row
  payForm.total_amount = 0
  payForm.insurance_amount = 0
  payForm.self_pay_amount = null
  payDialogVisible.value = true
}

async function onPay() {
  if (!selected.value) return
  payDialogLoading.value = true
  try {
    await payVisit(selected.value.visit_id, {
      total_amount: payForm.total_amount,
      insurance_amount: payForm.insurance_amount,
      self_pay_amount: payForm.self_pay_amount ?? undefined,
    })
    ElMessage.success('缴费成功')
    payDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e?.message || '缴费失败')
  } finally {
    payDialogLoading.value = false
  }
}

function getStatusType(status) {
  switch (status) {
    case '候诊中': return 'warning'
    case '就诊中': return 'primary'
    case '待缴费': return 'danger'
    case '已离院': return 'success'
    default: return 'info'
  }
}

onMounted(load)
</script>

<template>
  <div class="page-container">
    <el-card class="box-card" shadow="hover">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <el-icon class="header-icon"><FirstAidKit /></el-icon>
             <span>前台工作台 - 就诊管理</span>
           </div>
           <el-button :icon="Refresh" circle @click="load" />
        </div>
      </template>

      <div class="filter-bar">
        <span class="filter-label">状态筛选:</span>
        <el-select v-model="statusFilter" clearable placeholder="全部状态" style="width: 180px">
            <el-option label="候诊中" value="候诊中" />
            <el-option label="就诊中" value="就诊中" />
            <el-option label="待缴费" value="待缴费" />
            <el-option label="已离院" value="已离院" />
        </el-select>
        <el-button type="primary" :loading="loading" :icon="Search" @click="load" style="margin-left: 10px">刷新列表</el-button>
      </div>

      <el-table :data="visits" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="visit_id" label="就诊号" width="80" align="center" sortable />
        <el-table-column label="患者" width="120">
          <template #default="{ row }">{{ row.patient?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="电话" width="130">
          <template #default="{ row }">{{ row.patient?.phone || '-' }}</template>
        </el-table-column>
        <el-table-column label="诊室" width="100" align="center">
          <template #default="{ row }">{{ row.room?.room_number || '-' }}</template>
        </el-table-column>
        <el-table-column label="医生" width="120">
          <template #default="{ row }">{{ row.doctor?.name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
             <el-tag :type="getStatusType(row.status)" size="small" effect="light" round>
               {{ row.status }}
             </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="260" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
              <el-button 
                v-if="row.status === '候诊中'" 
                size="small" 
                type="primary" 
                plain
                @click="toStatus(row, '就诊中')"
              >
                开始就诊
              </el-button>
              <el-button 
                v-if="row.status === '就诊中'" 
                size="small" 
                type="warning" 
                plain
                @click="toStatus(row, '待缴费')"
              >
                结束就诊
              </el-button>
              <el-button 
                v-if="row.status === '待缴费'" 
                size="small" 
                type="success" 
                :icon="Money"
                @click="openPay(row)"
              >
                缴费结算
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="payDialogVisible" title="缴费结算" width="460px" destroy-on-close align-center>
      <el-form :model="payForm" label-width="120px" size="large" class="pay-form">
        <el-form-item label="总金额">
          <el-input-number v-model="payForm.total_amount" :min="0" :step="10" :prefix-icon="Money" style="width: 100%" />
        </el-form-item>
        <el-form-item label="医保支付">
          <el-input-number v-model="payForm.insurance_amount" :min="0" :step="10" :prefix-icon="CreditCard" style="width: 100%" />
        </el-form-item>
        <el-form-item label="自费支付">
          <el-input-number v-model="payForm.self_pay_amount" :min="0" :step="10" :prefix-icon="Wallet" style="width: 100%" placeholder="自动计算" />
          <div class="hint">若不填则自动计算：自费 = 总额 - 医保</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="payDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="payDialogLoading" @click="onPay">确认缴费</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-container {
  padding-bottom: 20px;
}

.box-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.header-icon {
  margin-right: 8px;
  color: var(--el-color-primary);
  font-size: 18px;
}

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
}

.pay-form {
  padding: 10px;
}

.hint {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  margin-top: 5px;
}
</style>

