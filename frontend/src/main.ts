import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import { createDiscreteApi } from 'naive-ui'
import 'nprogress/nprogress.css'
import './style.css'

// 创建Naive UI离散API
const { message, notification, dialog } = createDiscreteApi(
  ['message', 'notification', 'dialog']
)

const app = createApp(App)

// 全局配置
app.provide('message', message)
app.provide('notification', notification)
app.provide('dialog', dialog)

// 使用插件
app.use(router)
app.use(pinia)

app.mount('#app')
