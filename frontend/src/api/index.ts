import axios from 'axios'
import NProgress from 'nprogress'

// 创建Axios实例
// 使用相对路径，请求会自动通过Nginx代理转发
const api = axios.create({
  baseURL: '',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 显示进度条
    NProgress.start()
    
    // 添加Authorization头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    NProgress.done()
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    NProgress.done()
    return response.data
  },
  (error) => {
    NProgress.done()

    console.log('=== API 错误拦截 ===')
    console.log('错误状态码:', error.response?.status)
    console.log('错误URL:', error.config?.url)
    console.log('当前路径:', window.location.pathname)

    // 处理401错误 - 只在非登录页时才重定向
    if (error.response?.status === 401) {
      console.log('收到401错误')
      // 只有当前不在登录页时才清除token并重定向
      if (window.location.pathname !== '/login') {
        console.log('清除token并重定向到登录页')
        localStorage.removeItem('token')
        window.location.href = '/login'
      } else {
        console.log('已在登录页，不处理')
      }
    }

    return Promise.reject(error)
  }
)

export default api