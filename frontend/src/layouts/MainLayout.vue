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
          <span class="nav-icon">{{ item.icon }}</span>
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
          <button class="logout-btn" @click="logout">退出登录</button>
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

const router = useRouter()
const route = useRoute()

// 菜单配置
const menuItems = [
  { path: '/dashboard', label: '仪表盘', icon: '📊' },
  { path: '/products', label: '产品管理', icon: '📦' },
  { path: '/licenses', label: '授权管理', icon: '🔑' },
  { path: '/clients', label: '客户端管理', icon: '💻' },
  { path: '/audit-logs', label: '审计日志', icon: '📋' }
]

// 当前页面标题
const currentPageTitle = computed(() => {
  const currentRoute = menuItems.find(item => item.path === route.path)
  return currentRoute?.label || 'hex-auth'
})

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
  font-size: 18px;
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

.logout-btn {
  padding: 8px 16px;
  background-color: #ef4444;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.logout-btn:hover {
  background-color: #dc2626;
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