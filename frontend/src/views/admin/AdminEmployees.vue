<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

import { listDepartments } from '../../api/patient'
import { createEmployee, listEmployees, updateEmployee } from '../../api/admin'

const loading = ref(false)
const employees = ref([])
const deptOptions = ref([])

const dialogVisible = ref(false)
const dialogLoading = ref(false)
const editing = ref(null)

const formRef = ref()

const form = reactive({
  emp_id: '',
  name: '',
  gender: '男',
  phone: '',
  position: '医生',
  title: '',
  dept_id: null,
  status: '在职',
})

const rules = {
  emp_id: [{ required: true, message: '请填写工号', trigger: 'blur' }],
  name: [{ required: true, message: '请填写姓名', trigger: 'blur' }],
  phone: [
    {
      validator: (rule, value, callback) => {
        // 电话可选：有值才校验
        if (!value) return callback()
        const ok = /^1[3-9]\d{9}$/.test(String(value).trim())
        ok ? callback() : callback(new Error('请输入合法的11位手机号'))
      },
      trigger: 'blur',
    },
  ],
}

const positions = ['医生', '护士', '前台', '管理员']
const statuses = ['在职', '离职', '休假']

const deptName = computed(
  () => (deptId) => deptOptions.value.find((d) => d.dept_id === deptId)?.dept_name || ''
)

async function load() {
  loading.value = true
  try {
    const [depts, list] = await Promise.all([listDepartments(), listEmployees()])
    deptOptions.value = depts
    employees.value = list
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.emp_id = ''
  form.name = ''
  form.gender = '男'
  form.phone = ''
  form.position = '医生'
  form.title = ''
  form.dept_id = null
  form.status = '在职'

  // 清理校验状态（对话框 destroy-on-close 时也可不写，但写了更稳）
  if (formRef.value?.clearValidate) formRef.value.clearValidate()
}

function openCreate() {
  editing.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = row
  form.emp_id = row.emp_id
  form.name = row.name
  form.gender = row.gender
  form.phone = row.phone || ''
  form.position = row.position
  form.title = row.title || ''
  form.dept_id = row.dept_id
  form.status = row.status

  if (formRef.value?.clearValidate) formRef.value.clearValidate()
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value?.validate?.()
  if (!valid) return

  dialogLoading.value = true
  try {
    if (editing.value) {
      await updateEmployee(form.emp_id, {
        name: form.name,
        gender: form.gender,
        phone: form.phone ? String(form.phone).trim() : null,
        position: form.position,
        title: form.title || null,
        dept_id: form.dept_id,
        status: form.status,
      })
      ElMessage.success('已更新')
    } else {
      await createEmployee({
        emp_id: form.emp_id,
        name: form.name,
        gender: form.gender,
        phone: form.phone ? String(form.phone).trim() : null,
        position: form.position,
        title: form.title || null,
        dept_id: form.dept_id,
        status: form.status,
      })
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e?.message || '提交失败')
  } finally {
    dialogLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <el-space direction="vertical" fill size="large">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">员工管理</div>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增员工</el-button>
        </div>
      </template>

      <el-table :data="employees" v-loading="loading" style="width: 100%">
        <el-table-column prop="emp_id" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="position" label="岗位" width="100" />
        <el-table-column prop="title" label="职称" width="120" />
        <el-table-column label="科室" width="140">
          <template #default="{ row }">{{ row.dept_name || deptName(row.dept_id) || '-' }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" min-width="140" />
        <el-table-column prop="status" label="状态" width="90" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editing ? '编辑员工' : '新增员工'"
      width="560px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="工号" prop="emp_id">
          <el-input v-model="form.emp_id" :disabled="!!editing" />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>

        <el-form-item label="性别">
          <el-select v-model="form.gender" style="width: 100%">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>

        <el-form-item label="岗位">
          <el-select v-model="form.position" style="width: 100%">
            <el-option v-for="p in positions" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>

        <el-form-item label="职称">
          <el-input v-model="form.title" placeholder="可选" />
        </el-form-item>

        <el-form-item label="科室">
          <el-select v-model="form.dept_id" clearable placeholder="可选" style="width: 100%">
            <el-option v-for="d in deptOptions" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
          </el-select>
        </el-form-item>

        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="可选（11位手机号）" />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
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
