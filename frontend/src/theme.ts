import type { GlobalThemeOverrides } from 'naive-ui'

/**
 * 全站唯一的主题定义：单一强调色（蓝）+ 统一圆角体系。
 * 登录页、布局与各页面的自定义样式均从此取色，避免多套色板混用。
 */
export const brand = {
  primary: '#2563eb',
  primaryHover: '#3b82f6',
  primaryPressed: '#1d4ed8',
  primarySoft: 'rgba(37, 99, 235, 0.08)',

  ink: '#0f172a',
  inkSoft: '#1e293b',
  text: '#111827',
  textSecondary: '#475569',
  textTertiary: '#94a3b8',

  bg: '#f6f7f9',
  card: '#ffffff',
  border: '#e5e7eb',

  danger: '#dc2626',
  success: '#059669'
}

export const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: brand.primary,
    primaryColorHover: brand.primaryHover,
    primaryColorPressed: brand.primaryPressed,
    primaryColorSuppl: brand.primaryHover,
    borderRadius: '8px',
    fontWeightStrong: '600'
  }
}
