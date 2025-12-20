<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Calendar } from '@element-plus/icons-vue'

import { listDepartments } from '../api/patient'
import { onsiteRegister } from '../api/receptionist'

const deptOptions = ref([])
const loading = ref(false)

const form = reactive({
  name: '',
  phone: '',
  gender: '',
  id_card: '',
  dept_id: null,
  expected_time: '',
})

async function loadDepartments() {
  try {
    deptOptions.value = await listDepartments()
  } catch (e) {
    deptOptions.value = []
    ElMessage.error(e?.message || '加载科室失败')
  }
}

async function onSubmit() {
  if (!form.name || !form.phone || !form.dept_id) {
    ElMessage.warning('请填写姓名、电话和科室')
    return
  }

  loading.value = true
  try {
    const visit = await onsiteRegister({
      name: form.name,
      phone: form.phone,
      dept_id: form.dept_id,
      gender: form.gender || undefined,
      id_card: form.id_card || undefined,
      expected_time: form.expected_time || undefined,
    })
    ElMessage.success(`登记成功：Visit ${visit.visit_id}，诊室 ${visit.room?.room_number || '-'}，医生 ${visit.doctor?.name || '-'}`)

    // keep patient info, reset dept/time for next
    form.name = ''
    form.phone = ''
    form.gender = ''
    form.id_card = ''
    form.dept_id = null
    form.expected_time = ''
  } catch (e) {
    ElMessage.error(e?.message || '登记失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadDepartments)
</script>

<template>
  <el-card class="box-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon class="header-icon"><Plus /></el-icon>
        <span>挂号登记（到院就诊）</span>
      </div>
    </template>

    <el-form :model="form" label-position="top" size="large">
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <el-form-item label="姓名">
            <el-input v-model="form.name" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item label="联系电话">
            <el-input v-model="form.phone" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <el-form-item label="性别(可选)">
            <el-select v-model="form.gender" clearable placeholder="请选择" style="width: 100%">
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item label="身份证(可选)">
            <el-input v-model="form.id_card" placeholder="用于核验" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <el-form-item label="就诊科室">
            <el-select v-model="form.dept_id" placeholder="请选择科室" style="width: 100%">
              <el-option v-for="d in deptOptions" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item label="到达时间(可选)">
            <el-date-picker
              v-model="form.expected_time"
              type="datetime"
              placeholder="不填则默认当前时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 100%"
              :prefix-icon="Calendar"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <div class="form-actions">
        <el-button type="primary" class="submit-btn" :loading="loading" @click="onSubmit">提交登记</el-button>
      </div>
    </el-form>
  </el-card>
</template>

<style scoped>
.box-card {
  border-radius: 8px;
}
.card-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}
.header-icon {
  margin-right: 8px;
  color: var(--el-color-primary);
}
.form-actions {
  margin-top: 10px;
}
.submit-btn {
  width: 100%;
  font-weight: 600;
  letter-spacing: 1px;
}
</style>

