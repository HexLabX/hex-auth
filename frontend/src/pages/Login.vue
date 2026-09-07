<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="handleLogin">
      <div class="brand-mark">
        <Icon :icon="icons.licenses" />
      </div>
      <h1 class="login-title">登录到 hex-auth</h1>
      <p class="login-subtitle">授权中心管理后台</p>

      <div class="form-group">
        <label for="username">用户名</label>
        <input
          id="username"
          type="text"
          v-model="loginForm.username"
          placeholder="请输入用户名"
          autocomplete="username"
          required
        >
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <input
          id="password"
          type="password"
          v-model="loginForm.password"
          placeholder="请输入密码"
          autocomplete="current-password"
          required
        >
      </div>

      <p v-if="error" class="error-message" role="alert">{{ error }}</p>

      <button type="submit" class="login-btn" :disabled="isLoading">
        {{ isLoading ? '登录中...' : '登录' }}
      </button>
    </form>

    <p class="page-footer">统一在线授权中心</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import icons from '@/icons'
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

    // 如果响应是字符串，尝试解析
    let data = response
    if (typeof response === 'string') {
      try {
        data = JSON.parse(response)
      } catch {
        // 保持data为原始response，由下方判断处理
      }
    }

    // 保存token
    if (data && data.access_token) {
      localStorage.setItem('token', data.access_token)
      isLoading.value = false
      await router.push('/dashboard')
    } else {
      error.value = '登录失败：无效的响应'
      isLoading.value = false
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '登录失败，请检查用户名和密码'
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  padding: 24px;
  background-color: #f6f7f9;
  background-image: radial-gradient(circle, #e3e5e9 1px, transparent 1px);
  background-size: 22px 22px;
}

.login-card {
  width: 100%;
  max-width: 328px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 32px 28px 28px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

@media (prefers-reduced-motion: no-preference) {
  .login-card {
    animation: card-in 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes card-in {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}

.brand-mark {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background-color: #111827;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.brand-mark :deep(svg) {
  width: 19px;
  height: 19px;
  color: #fff;
}

.login-title {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #111827;
  text-align: center;
}

.login-subtitle {
  margin: 6px 0 26px;
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-bottom: 16px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}

.form-group input {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #111827;
  background-color: #fff;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form-group input::placeholder {
  color: #9ca3af;
}

.form-group input:hover {
  border-color: #9ca3af;
}

.form-group input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.login-btn {
  width: 100%;
  margin-top: 8px;
  padding: 11px;
  background-color: #111827;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s ease, transform 0.1s ease;
}

.login-btn:hover:not(:disabled) {
  background-color: #1f2937;
}

.login-btn:active:not(:disabled) {
  transform: scale(0.99);
}

.login-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.error-message {
  margin: 0 0 14px;
  color: #dc2626;
  font-size: 13px;
}

.page-footer {
  position: absolute;
  bottom: 24px;
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}
</style>
