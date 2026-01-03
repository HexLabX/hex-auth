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
    
    // 处理401错误
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default api