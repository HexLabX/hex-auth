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

    console.log('=== 登录调试信息 ===')
    console.log('原始响应:', response)

    // 如果响应是字符串，尝试解析
    let data = response
    if (typeof response === 'string') {
      console.log('响应是字符串，尝试解析')
      try {
        data = JSON.parse(response)
      } catch (e) {
        console.error('JSON解析失败:', e)
      }
    }

    // 保存token
    if (data && data.access_token) {
      // 保存 token 到 localStorage
      localStorage.setItem('token', data.access_token)
      console.log('✓ Token已保存')

      // 验证 token 已保存
      const token = localStorage.getItem('token')
      console.log('✓ Token验证:', token ? '成功' : '失败')

      // 先设置 isLoading 为 false
      isLoading.value = false

      // 等待确保所有操作完成
      await new Promise(resolve => setTimeout(resolve, 100))

      // 使用 Vue Router 导航，不刷新页面
      console.log('→ 准备跳转到 /dashboard')
      await router.push('/dashboard')
      console.log('✓ 跳转完成')
    } else {
      console.error('✗ 响应中没有 access_token')
      error.value = '登录失败：无效的响应'
      isLoading.value = false
    }
  } catch (err: any) {
    console.error('=== 登录错误 ===')
    console.error('错误对象:', err)
    console.error('错误消息:', err.message)

    error.value = err.response?.data?.detail || err.message || '登录失败，请检查用户名和密码'
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