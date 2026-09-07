import { createDiscreteApi } from 'naive-ui'
import { themeOverrides } from '@/theme'

const { message, notification, dialog } = createDiscreteApi(
  ['message', 'notification', 'dialog'],
  { configProviderProps: { themeOverrides } }
)

export { message, notification, dialog }

// 便捷方法
export const Message = {
  success(content: string, duration = 3000) {
    message.success(content, { duration })
  },

  error(content: string, duration = 5000) {
    message.error(content, { duration })
  },

  warning(content: string, duration = 4000) {
    message.warning(content, { duration })
  },

  info(content: string, duration = 3000) {
    message.info(content, { duration })
  },

  loading(content: string = '加载中...') {
    return message.loading(content, { duration: 0 })
  }
}

export const Notification = {
  success(title: string, content?: string, duration = 5000) {
    notification.success({ title, content, duration })
  },

  error(title: string, content?: string, duration = 5000) {
    notification.error({ title, content, duration })
  },

  warning(title: string, content?: string, duration = 5000) {
    notification.warning({ title, content, duration })
  },

  info(title: string, content?: string, duration = 5000) {
    notification.info({ title, content, duration })
  }
}

export const Dialog = {
  confirm(options: { title: string; content: string }) {
    return new Promise<boolean>((resolve) => {
      dialog.warning({
        title: options.title,
        content: options.content,
        positiveText: '确定',
        negativeText: '取消',
        onPositiveClick: () => resolve(true),
        onNegativeClick: () => resolve(false),
        onClose: () => resolve(false)
      })
    })
  },

  alert(options: { title: string; content: string }) {
    return new Promise<boolean>((resolve) => {
      dialog.info({
        title: options.title,
        content: options.content,
        positiveText: '确定',
        onPositiveClick: () => resolve(true),
        onClose: () => resolve(true)
      })
    })
  }
}