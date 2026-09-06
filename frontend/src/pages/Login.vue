<template>
  <div class="login-page">
    <!-- 左侧品牌面板（窄屏隐藏） -->
    <div class="brand-panel">
      <div class="brand-inner">
        <div class="brand-mark">
          <Icon :icon="icons.licenses" />
        </div>
        <h1 class="brand-name">hex-auth</h1>
        <p class="brand-slogan">统一在线授权中心</p>
        <ul class="brand-features">
          <li>
            <Icon :icon="icons.check" />
            <span>多产品独立密钥与授权签发</span>
          </li>
          <li>
            <Icon :icon="icons.check" />
            <span>设备绑定、心跳与远程禁用</span>
          </li>
          <li>
            <Icon :icon="icons.check" />
            <span>关键操作全程审计</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="form-panel">
      <form class="login-form" @submit.prevent="handleLogin">
        <h2 class="form-title">管理后台登录</h2>
        <p class="form-subtitle">使用管理员账号进入 hex-auth 控制台</p>

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
    </div>
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
  display: flex;
  width: 100%;
  height: 100%;
  min-height: 100dvh;
  background-color: #fff;
}

/* ---------- 左侧品牌面板 ---------- */
.brand-panel {
  width: 45%;
  max-width: 640px;
  background-color: #0f172a;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
  background-size: 36px 36px;
  color: #fff;
  display: flex;
  align-items: center;
}

.brand-inner {
  padding: 48px 56px;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background-color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.brand-mark :deep(svg) {
  width: 22px;
  height: 22px;
  color: #fff;
}

.brand-name {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.brand-slogan {
  margin: 8px 0 40px;
  font-size: 15px;
  color: #94a3b8;
}

.brand-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.brand-features li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #cbd5e1;
}

.brand-features li :deep(svg) {
  width: 16px;
  height: 16px;
  color: #34d399;
  flex-shrink: 0;
}

/* ---------- 右侧表单区 ---------- */
.form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.login-form {
  width: 100%;
  max-width: 360px;
}

@media (prefers-reduced-motion: no-preference) {
  .login-form {
    animation: form-in 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes form-in {
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

.form-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #111827;
}

.form-subtitle {
  margin: 8px 0 32px;
  font-size: 14px;
  color: #64748b;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.form-group input {
  padding: 11px 12px;
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
  padding: 12px;
  background-color: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s ease, transform 0.1s ease;
}

.login-btn:hover:not(:disabled) {
  background-color: #3b82f6;
}

.login-btn:active:not(:disabled) {
  transform: scale(0.99);
}

.login-btn:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

.error-message {
  margin: -8px 0 12px;
  color: #dc2626;
  font-size: 13px;
}

/* ---------- 窄屏回退：隐藏品牌面板 ---------- */
@media (max-width: 900px) {
  .brand-panel {
    display: none;
  }

  .form-panel {
    background-color: #f6f7f9;
  }

  .login-form {
    background-color: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 32px 28px;
  }
}
</style>
