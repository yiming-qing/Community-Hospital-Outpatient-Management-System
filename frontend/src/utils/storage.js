const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

/**
 * 获取 token
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

/**
 * 获取当前用户
 */
export function getUser() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

/**
 * 登录 / 注册成功后调用
 * 写入 token + user，并通知全站认证状态已变化
 */
export function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))

  // ⭐ 关键：通知所有监听者（Header / Layout 等）
  window.dispatchEvent(new Event('auth-changed'))
}

/**
 * 退出登录时调用
 * 清空认证信息，并通知全站
 */
export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)

  // ⭐ 关键：通知所有监听者（Header / Layout 等）
  window.dispatchEvent(new Event('auth-changed'))
}
