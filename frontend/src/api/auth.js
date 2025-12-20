import http, { unwrap } from './http'

export async function login(username, password) {
  const resp = await http.post('/api/auth/login', { username, password })
  return unwrap(resp)
}

export async function register(payload) {
  const resp = await http.post('/api/auth/register', payload)
  return unwrap(resp)
}

export async function profile() {
  const resp = await http.get('/api/auth/profile')
  return unwrap(resp)
}
