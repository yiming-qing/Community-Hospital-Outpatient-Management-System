<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { register } from '../api/auth'
import { setAuth } from '../utils/storage'
import { phoneRules } from '../utils/validators'

const router = useRouter()
const loading = ref(false)
const formRef = ref()

const form = reactive({
  username: '',
  password: '',
  name: '',
  phone: '',
  gender: '',
  id_card: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少 3 位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
  ],
  phone: phoneRules,
}

async function onSubmit() {
  const valid = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    const data = await register({
      username: form.username,
      password: form.password,
      name: form.name,
      phone: form.phone,
      gender: form.gender || undefined,
      id_card: form.id_card || undefined,
    })
    setAuth(data.access_token, data.user)
    ElMessage.success('注册成功')
    router.replace('/')
  } catch (e) {
    ElMessage.error(e?.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <el-card class="card">
      <template #header>
        <div class="title">患者注册</div>
      </template>

      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="90px"
        @submit.prevent="onSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="至少 3 位" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="至少 6 位"
            show-password
          />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>

        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>

        <el-form-item label="性别(可选)">
          <el-select v-model="form.gender" clearable placeholder="请选择" style="width: 100%">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>

        <el-form-item label="身份证(可选)">
          <el-input v-model="form.id_card" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="onSubmit">
            注册并登录
          </el-button>
          <el-button text @click="$router.push('/login')">
            已有账号？去登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}
.card {
  width: 480px;
}
.title {
  font-weight: 700;
}
</style>
