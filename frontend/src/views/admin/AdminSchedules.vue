<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'

import { listDepartments } from '../../api/patient'
import { createSchedule, deleteSchedule, listEmployees, listRooms, listSchedules, updateSchedule } from '../../api/admin'

const loading = ref(false)
const schedules = ref([])
const rooms = ref([])
const employees = ref([])
const deptOptions = ref([])

const filters = reactive({
  work_date: '',
})

const doctors = computed(() => employees.value.filter((e) => e.position === '医生'))

const dialogVisible = ref(false)
const dialogLoading = ref(false)
const editing = ref(null)

const form = reactive({
  room_id: null,
  doctor_id: '',
  work_date: '',
  time_slot: '上午',
  max_patients: 30,
})

async function loadAll() {
  loading.value = true
  try {
    const [deptList, roomList, employeeList, scheduleList] = await Promise.all([
      listDepartments(),
      listRooms(),
      listEmployees(),
      listSchedules(filters.work_date ? { work_date: filters.work_date } : {}),
    ])
    deptOptions.value = deptList
    rooms.value = roomList
    employees.value = employeeList
    schedules.value = scheduleList
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.room_id = null
  form.doctor_id = ''
  form.work_date = ''
  form.time_slot = '上午'
  form.max_patients = 30
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = row
  form.room_id = row.room_id
  form.doctor_id = row.doctor_id
  form.work_date = row.work_date
  form.time_slot = row.time_slot
  form.max_patients = row.max_patients
  dialogVisible.value = true
}

async function onSubmit() {
  if (!form.room_id || !form.doctor_id || !form.work_date || !form.time_slot) {
    ElMessage.warning('请填写诊室、医生、日期和时间段')
    return
  }
  dialogLoading.value = true
  try {
    if (editing.value) {
      await updateSchedule(editing.value.schedule_id, {
        room_id: form.room_id,
        doctor_id: form.doctor_id,
        work_date: form.work_date,
        time_slot: form.time_slot,
        max_patients: form.max_patients,
      })
      ElMessage.success('已更新')
    } else {
      await createSchedule({
        room_id: form.room_id,
        doctor_id: form.doctor_id,
        work_date: form.work_date,
        time_slot: form.time_slot,
        max_patients: form.max_patients,
      })
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    await loadAll()
  } catch (e) {
    ElMessage.error(e?.message || '提交失败')
  } finally {
    dialogLoading.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`删除排班 ${row.schedule_id}？`, '确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteSchedule(row.schedule_id)
    ElMessage.success('已删除')
    await loadAll()
  } catch (e) {
    ElMessage.error(e?.message || '删除失败')
  }
}

function deptName(deptId) {
  const d = deptOptions.value.find((x) => x.dept_id === deptId)
  return d?.dept_name || ''
}

onMounted(loadAll)
</script>

<template>
  <el-space direction="vertical" fill size="large">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">排班管理</div>
          <el-space>
            <el-date-picker v-model="filters.work_date" type="date" value-format="YYYY-MM-DD" placeholder="按日期筛选" />
            <el-button :icon="Refresh" @click="loadAll">刷新</el-button>
            <el-button type="primary" :icon="Plus" @click="openCreate">新增排班</el-button>
          </el-space>
        </div>
      </template>

      <el-table :data="schedules" v-loading="loading" style="width: 100%">
        <el-table-column prop="schedule_id" label="ID" width="80" />
        <el-table-column prop="work_date" label="日期" width="120" />
        <el-table-column prop="time_slot" label="时间段" width="100" />
        <el-table-column prop="room_number" label="诊室" width="100" />
        <el-table-column label="科室" width="140">
          <template #default="{ row }">{{ row.dept_name || deptName(row.dept_id) || '-' }}</template>
        </el-table-column>
        <el-table-column label="医生" min-width="160">
          <template #default="{ row }">{{ row.doctor_name ? `${row.doctor_name} (${row.doctor_id})` : row.doctor_id }}</template>
        </el-table-column>
        <el-table-column prop="max_patients" label="容量" width="90" />
        <el-table-column prop="current_patients" label="已占用" width="90" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button size="small" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="onDelete(row)">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑排班' : '新增排班'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="日期">
          <el-date-picker v-model="form.work_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="时间段">
          <el-select v-model="form.time_slot" style="width: 100%">
            <el-option label="上午" value="上午" />
            <el-option label="下午" value="下午" />
            <el-option label="全天" value="全天" />
          </el-select>
        </el-form-item>
        <el-form-item label="诊室">
          <el-select v-model="form.room_id" placeholder="请选择" style="width: 100%">
            <el-option
              v-for="r in rooms"
              :key="r.room_id"
              :label="`${r.room_number} - ${r.dept_name || deptName(r.dept_id)}`"
              :value="r.room_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="医生">
          <el-select v-model="form.doctor_id" placeholder="请选择" filterable style="width: 100%">
            <el-option
              v-for="d in doctors"
              :key="d.emp_id"
              :label="`${d.name} (${d.emp_id}) - ${d.dept_name || deptName(d.dept_id) || '无科室'}`"
              :value="d.emp_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="容量">
          <el-input-number v-model="form.max_patients" :min="1" :max="200" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </el-space>
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
</style>

