import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createDiscreteApi } from 'naive-ui'
import { themeOverrides } from './theme'
import 'nprogress/nprogress.css'
import './style.css'

// 创建Naive UI离散API（与全局主题保持一致）
const { message, notification, dialog } = createDiscreteApi(
  ['message', 'notification', 'dialog'],
  { configProviderProps: { themeOverrides } }
)

const app = createApp(App)

// 全局配置
app.provide('message', message)
app.provide('notification', notification)
app.provide('dialog', dialog)

app.use(router)

app.mount('#app')
