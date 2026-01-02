<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <div class="login-header">
        <h1>hex-auth</h1>
        <p>统一在线授权中心</p>
      </div>
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="loginForm.username"
            placeholder="请输入用户名"
            required
          >
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="loginForm.password"
            placeholder="请输入密码"
            required
          >
        </div>
        <div class="form-actions">
          <button type="submit" class="login-btn" :disabled="isLoading">
            {{ isLoading ? '登录中...' : '登录' }}
          </button>
        </div>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

const loginForm = ref({
  username: '',
  password: ''
})

const isLoading = ref(false)
const error = ref('')

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    // 调用登录API
    const response = await api.post('/admin/auth/login', new URLSearchParams({
      username: loginForm.value.username,
      password: loginForm.value.password
    }))
    
    // 保存token
    if (response.access_token) {
      localStorage.setItem('token', response.access_token)
      router.push('/dashboard')
    } else {
      error.value = '登录失败：无效的响应'
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-color: #f5f7fa;
}

.login-form-wrapper {
  width: 100%;
  max-width: 400px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 32px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.login-header p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.form-group input {
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-actions {
  margin-top: 8px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background-color: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.login-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.login-btn:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

.error-message {
  margin-top: 16px;
  color: #ef4444;
  font-size: 14px;
  text-align: center;
}
</style>