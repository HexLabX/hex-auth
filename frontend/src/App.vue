<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 页面加载时检查登录状态
onMounted(() => {
  const token = localStorage.getItem('token')
  const currentPath = window.location.pathname
  
  // 如果没有token且不在登录页，跳转到登录页
  if (!token && currentPath !== '/login') {
    router.push('/login')
  }
  
  // 如果有token且在登录页，跳转到首页
  if (token && currentPath === '/login') {
    router.push('/dashboard')
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #f5f7fa;
  color: #1e293b;
}

#app {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

/* 全屏模式优化 */
body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}

html {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
