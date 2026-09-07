<template>
  <!-- abstract：不渲染包装div，保持 height:100% 链条不被破坏 -->
  <n-config-provider abstract :theme-overrides="themeOverrides">
    <div id="app">
      <router-view />
    </div>
  </n-config-provider>
</template>

<script setup lang="ts">
import { NConfigProvider } from 'naive-ui'
import { themeOverrides } from './theme'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background-color: #f6f7f9;
  color: #111827;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100%;
  height: 100%;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
