<template>
  <div class="profile-page">
    <div class="profile-container">
      <!-- 用户信息卡片 -->
      <div class="info-card">
        <h2>个人信息</h2>
        <div class="info-list">
          <div class="info-item">
            <span class="info-label">用户名</span>
            <span class="info-value">{{ userInfo.username }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">状态</span>
            <span class="info-value">
              <span class="status-badge active">
                <Icon :icon="icons.check" />
                {{ userInfo.status === 'active' ? '正常' : '禁用' }}
              </span>
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">最后登录</span>
            <span class="info-value">{{ formatDate(userInfo.last_login) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">创建时间</span>
            <span class="info-value">{{ formatDate(userInfo.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- 修改密码卡片 -->
      <div class="password-card">
        <h2>修改密码</h2>
        <form class="password-form" @submit.prevent="handleChangePassword">
          <div class="form-group">
            <label for="old_password">旧密码</label>
            <input
              type="password"
              id="old_password"
              v-model="passwordForm.old_password"
              placeholder="请输入旧密码"
              required
            />
          </div>
          <div class="form-group">
            <label for="new_password">新密码</label>
            <input
              type="password"
              id="new_password"
              v-model="passwordForm.new_password"
              placeholder="请输入新密码（至少6位）"
              required
              minlength="6"
            />
          </div>
          <div class="form-group">
            <label for="confirm_password">确认新密码</label>
            <input
              type="password"
              id="confirm_password"
              v-model="passwordForm.confirm_password"
              placeholder="请再次输入新密码"
              required
              minlength="6"
            />
          </div>
          <div v-if="error" class="error-message">
            <Icon :icon="icons.warning" />
            {{ error }}
          </div>
          <div v-if="success" class="success-message">
            <Icon :icon="icons.check" />
            {{ success }}
          </div>
          <div class="form-actions">
            <button type="submit" class="submit-btn" :disabled="isLoading">
              <Icon :icon="isLoading ? icons.loading : icons.edit" />
              {{ isLoading ? '提交中...' : '修改密码' }}
            </button>
            <button type="button" class="reset-btn" @click="resetForm" :disabled="isLoading">
              <Icon :icon="icons.close" />
              重置
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import icons from '@/icons'
import { Message } from '@/utils/message'
import api from '@/api'

// 用户信息
const userInfo = ref({
  username: '',
  status: '',
  last_login: '',
  created_at: ''
})

// 密码表单
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 状态
const isLoading = ref(false)
const error = ref('')
const success = ref('')

// 格式化日期
const formatDate = (dateString: string | Date) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await api.get('/admin/auth/me')
    userInfo.value = response
  } catch (err) {
    Message.error('获取用户信息失败')
  }
}

// 修改密码
const handleChangePassword = async () => {
  // 验证
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    error.value = '两次输入的密码不一致'
    success.value = ''
    return
  }

  if (passwordForm.value.new_password.length < 6) {
    error.value = '新密码长度不能少于6位'
    success.value = ''
    return
  }

  isLoading.value = true
  error.value = ''
  success.value = ''

  try {
    await api.post('/admin/auth/change-password', new URLSearchParams({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    }))

    success.value = '密码修改成功，下次登录时请使用新密码'
    Message.success('密码修改成功')

    // 清空表单
    resetForm()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '密码修改失败，请检查旧密码是否正确'
    Message.error(error.value)
  } finally {
    isLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
  error.value = ''
  success.value = ''
}

// 页面挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.profile-page {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 20px;
}

.profile-container {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card,
.password-card {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 32px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

.info-card h2,
.password-card h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 12px;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 6px;
}

.info-label {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
}

.info-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge :deep(svg) {
  width: 14px;
  height: 14px;
}

.password-form {
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
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.error-message,
.success-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
}

.error-message {
  background-color: #fee2e2;
  color: #991b1b;
}

.success-message {
  background-color: #d1fae5;
  color: #065f46;
}

.error-message :deep(svg),
.success-message :deep(svg) {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.submit-btn,
.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-btn :deep(svg),
.reset-btn :deep(svg) {
  width: 16px;
  height: 16px;
}

.submit-btn {
  background-color: #3b82f6;
  color: #fff;
  flex: 1;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.submit-btn:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

.reset-btn {
  background-color: #fff;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.reset-btn:hover:not(:disabled) {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}

.reset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
