<template>
  <div class="main-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>hex-auth</h1>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
        >
          <span class="nav-icon"><Icon :icon="item.icon" /></span>
          <span class="nav-text">{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>
    <main class="main-content">
      <header class="top-nav">
        <div class="nav-left">
          <h2>{{ currentPageTitle }}</h2>
        </div>
        <div class="nav-right">
          <button class="profile-btn" @click="goToProfile" title="个人中心">
            <Icon :icon="icons.user" />
            <span class="profile-text">个人中心</span>
          </button>
          <button class="logout-btn" @click="logout" title="退出登录">
            <Icon :icon="icons.logout" />
            <span class="logout-text">退出</span>
          </button>
        </div>
      </header>
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import icons from '@/icons'

const router = useRouter()
const route = useRoute()

// 菜单配置
const menuItems = [
  { path: '/dashboard', label: '仪表盘', icon: icons.dashboard },
  { path: '/products', label: '产品管理', icon: icons.products },
  { path: '/licenses', label: '授权管理', icon: icons.licenses },
  { path: '/clients', label: '客户端管理', icon: icons.clients },
  { path: '/audit-logs', label: '审计日志', icon: icons.auditLogs }
]

// 当前页面标题
const currentPageTitle = computed(() => {
  const currentRoute = menuItems.find(item => item.path === route.path)
  if (route.path === '/profile') return '个人中心'
  return currentRoute?.label || 'hex-auth'
})

// 跳转到个人中心
const goToProfile = () => {
  router.push('/profile')
}

// 退出登录
const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  display: flex;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background-color: #1e293b;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #334155;
}

.sidebar-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #cbd5e1;
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: #334155;
  color: #fff;
}

.nav-item.active {
  background-color: #3b82f6;
  color: #fff;
}

.nav-icon {
  margin-right: 12px;
  display: flex;
  align-items: center;
}

.nav-icon :deep(svg) {
  width: 18px;
  height: 18px;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-nav {
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.nav-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.nav-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.profile-btn,
.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.profile-btn :deep(svg),
.logout-btn :deep(svg) {
  width: 16px;
  height: 16px;
}

.profile-btn {
  background-color: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.profile-btn:hover {
  background-color: #e2e8f0;
  border-color: #cbd5e1;
}

.profile-text {
  display: inline-block;
}

.logout-btn {
  background-color: #ef4444;
  color: #fff;
}

.logout-btn:hover {
  background-color: #dc2626;
}

.logout-text {
  display: inline-block;
}

.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  box-sizing: border-box;
  /* 确保内容在全屏模式下能正确滚动 */
  min-height: 0;
}
</style>