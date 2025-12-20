<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

import { listDepartments } from '../../api/patient'
import { createRoom, listRooms, updateRoom } from '../../api/admin'

const loading = ref(false)
const rooms = ref([])
const deptOptions = ref([])

const dialogVisible = ref(false)
const dialogLoading = ref(false)
const editing = ref(null)

const form = reactive({
  room_number: '',
  dept_id: null,
  status: '启用',
})

async function load() {
  loading.value = true
  try {
    const [depts, roomList] = await Promise.all([listDepartments(), listRooms()])
    deptOptions.value = depts
    rooms.value = roomList
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.room_number = ''
  form.dept_id = null
  form.status = '启用'
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = row
  form.room_number = row.room_number
  form.dept_id = row.dept_id
  form.status = row.status
  dialogVisible.value = true
}

async function onSubmit() {
  if (!form.room_number || !form.dept_id) {
    ElMessage.warning('请填写诊室号和科室')
    return
  }
  dialogLoading.value = true
  try {
    if (editing.value) {
      await updateRoom(editing.value.room_id, {
        room_number: form.room_number,
        dept_id: form.dept_id,
        status: form.status,
      })
      ElMessage.success('已更新')
    } else {
      await createRoom({
        room_number: form.room_number,
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
          <div class="title">诊室管理</div>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增诊室</el-button>
        </div>
      </template>

      <el-table :data="rooms" v-loading="loading" style="width: 100%">
        <el-table-column prop="room_id" label="ID" width="80" />
        <el-table-column prop="room_number" label="诊室号" width="120" />
        <el-table-column prop="dept_name" label="科室" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑诊室' : '新增诊室'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="诊室号">
          <el-input v-model="form.room_number" />
        </el-form-item>
        <el-form-item label="科室">
          <el-select v-model="form.dept_id" placeholder="请选择" style="width: 100%">
            <el-option v-for="d in deptOptions" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="启用" value="启用" />
            <el-option label="停用" value="停用" />
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

