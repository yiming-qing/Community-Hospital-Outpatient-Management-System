<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'

import { listDepartments } from '../../api/patient'
import { getVisitMedicalRecord, listEmployees, searchVisits, upsertVisitMedicalRecord } from '../../api/admin'

const loading = ref(false)
const visits = ref([])
const total = ref(0)

const deptOptions = ref([])
const employees = ref([])
const doctors = computed(() => employees.value.filter((e) => e.position === '医生'))

const pagination = reactive({
  page: 1,
  pageSize: 20,
})

const form = reactive({
  visit_id: '',
  appt_id: '',
  name: '',
  phone: '',
  id_card: '',
  room_number: '',
  dept_id: null,
  doctor_id: '',
  status: '',
  start_date: '',
  end_date: '',
})

const recordDialogVisible = ref(false)
const recordDialogLoading = ref(false)
const recordVisit = ref(null)
const recordForm = reactive({
  diagnosis: '',
  treatment: '',
  prescription: '',
  note: '',
})

function buildParams() {
  const params = {
    limit: pagination.pageSize,
    offset: (pagination.page - 1) * pagination.pageSize,
    visit_id: form.visit_id || undefined,
    appt_id: form.appt_id || undefined,
    name: form.name || undefined,
    phone: form.phone || undefined,
    id_card: form.id_card || undefined,
    room_number: form.room_number || undefined,
    dept_id: form.dept_id ?? undefined,
    doctor_id: form.doctor_id || undefined,
    status: form.status || undefined,
    start_date: form.start_date || undefined,
    end_date: form.end_date || undefined,
  }
  return params
}

async function openMedicalRecord(row) {
  recordVisit.value = row
  recordDialogVisible.value = true
  recordDialogLoading.value = true
  try {
    const record = await getVisitMedicalRecord(row.visit_id)
    recordForm.diagnosis = record?.diagnosis || ''
    recordForm.treatment = record?.treatment || ''
    recordForm.prescription = record?.prescription || ''
    recordForm.note = record?.note || ''
  } catch (e) {
    ElMessage.error(e?.message || '加载病历失败')
  } finally {
    recordDialogLoading.value = false
  }
}

async function saveMedicalRecord() {
  if (!recordVisit.value) return
  recordDialogLoading.value = true
  try {
    await upsertVisitMedicalRecord(recordVisit.value.visit_id, {
      diagnosis: recordForm.diagnosis || null,
      treatment: recordForm.treatment || null,
      prescription: recordForm.prescription || null,
      note: recordForm.note || null,
    })
    ElMessage.success('已保存')
    recordDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    recordDialogLoading.value = false
  }
}

async function load() {
  loading.value = true
  try {
    const resp = await searchVisits(buildParams())
    visits.value = resp.items || []
    total.value = resp.total || 0
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function onSearch() {
  pagination.page = 1
  await load()
}

function deptName(deptId) {
  const d = deptOptions.value.find((x) => x.dept_id === deptId)
  return d?.dept_name || ''
}

onMounted(async () => {
  try {
    const [depts, emps] = await Promise.all([listDepartments(), listEmployees()])
    deptOptions.value = depts
    employees.value = emps
  } catch (e) {
    ElMessage.error(e?.message || '加载基础数据失败')
  }
  await load()
})
</script>

<template>
  <el-space direction="vertical" fill size="large">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">就诊查询</div>
          <el-space>
            <el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button>
          </el-space>
        </div>
      </template>

      <el-form :model="form" label-width="90px">
        <el-row :gutter="12">
          <el-col :xs="24" :md="8">
            <el-form-item label="就诊号">
              <el-input v-model="form.visit_id" placeholder="visit_id" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="预约号">
              <el-input v-model="form.appt_id" placeholder="appt_id" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="状态">
              <el-select v-model="form.status" clearable placeholder="全部" style="width: 100%">
                <el-option label="候诊中" value="候诊中" />
                <el-option label="就诊中" value="就诊中" />
                <el-option label="待缴费" value="待缴费" />
                <el-option label="已离院" value="已离院" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :xs="24" :md="8">
            <el-form-item label="姓名">
              <el-input v-model="form.name" placeholder="模糊匹配" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="电话">
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="身份证">
              <el-input v-model="form.id_card" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :xs="24" :md="8">
            <el-form-item label="诊室号">
              <el-input v-model="form.room_number" placeholder="如 101" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="科室">
              <el-select v-model="form.dept_id" clearable placeholder="全部" style="width: 100%">
                <el-option v-for="d in deptOptions" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="医生">
              <el-select v-model="form.doctor_id" clearable filterable placeholder="全部" style="width: 100%">
                <el-option
                  v-for="d in doctors"
                  :key="d.emp_id"
                  :label="`${d.name} (${d.emp_id}) - ${d.dept_name || deptName(d.dept_id) || '无科室'}`"
                  :value="d.emp_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :xs="24" :md="8">
            <el-form-item label="开始日期">
              <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8" class="actions">
            <el-button type="primary" :icon="Search" :loading="loading" @click="onSearch">查询</el-button>
          </el-col>
        </el-row>
      </el-form>

      <el-table :data="visits" v-loading="loading" style="width: 100%">
        <el-table-column prop="visit_id" label="就诊号" width="90" />
        <el-table-column prop="appt_id" label="预约号" width="90" />
        <el-table-column label="患者" width="120">
          <template #default="{ row }">{{ row.patient?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="电话" width="140">
          <template #default="{ row }">{{ row.patient?.phone || '-' }}</template>
        </el-table-column>
        <el-table-column label="身份证" min-width="170">
          <template #default="{ row }">{{ row.patient?.id_card || '-' }}</template>
        </el-table-column>
        <el-table-column label="科室" width="140">
          <template #default="{ row }">{{ row.room?.dept_name || deptName(row.room?.dept_id) || '-' }}</template>
        </el-table-column>
        <el-table-column label="诊室" width="90" align="center">
          <template #default="{ row }">{{ row.room?.room_number || '-' }}</template>
        </el-table-column>
        <el-table-column label="医生" width="160">
          <template #default="{ row }">
            {{ row.doctor?.name ? `${row.doctor.name} (${row.doctor.emp_id})` : row.doctor?.emp_id || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="check_in_time" label="签到时间" width="170" />
        <el-table-column prop="checkout_time" label="离院时间" width="170" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openMedicalRecord(row)">病历</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @size-change="onSearch"
          @current-change="load"
        />
      </div>
    </el-card>
  </el-space>

  <el-dialog v-model="recordDialogVisible" title="病历管理" width="640px" destroy-on-close align-center>
    <el-alert
      v-if="recordVisit"
      :title="`就诊号：${recordVisit.visit_id}，患者：${recordVisit.patient?.name || '-'}，诊室：${recordVisit.room?.room_number || '-'}`"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 16px"
    />

    <el-form :model="recordForm" label-width="90px" v-loading="recordDialogLoading">
      <el-form-item label="诊断">
        <el-input v-model="recordForm.diagnosis" type="textarea" :rows="2" placeholder="可选" />
      </el-form-item>
      <el-form-item label="处置/治疗">
        <el-input v-model="recordForm.treatment" type="textarea" :rows="2" placeholder="可选" />
      </el-form-item>
      <el-form-item label="处方">
        <el-input v-model="recordForm.prescription" type="textarea" :rows="2" placeholder="可选" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="recordForm.note" type="textarea" :rows="2" placeholder="可选" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="recordDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="recordDialogLoading" @click="saveMedicalRecord">保存</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-weight: 700;
}
.actions {
  display: flex;
  align-items: center;
  height: 100%;
}
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>
