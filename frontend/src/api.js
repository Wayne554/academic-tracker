import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// 自动附加 token：直接从 localStorage 读取，避免循环依赖
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ========== 认证 ==========
export function loginApi(data) {
  return api.post('/auth/login', data)
}
export function getMe() {
  return api.get('/auth/me')
}

// ========== 期刊 ==========
export function getJournals(params = {}) {
  return api.get('/journals', { params })
}
export function getCategories() {
  return api.get('/journals/categories')
}
export function createJournal(data) {
  return api.post('/journals', data)
}
export function updateJournal(id, data) {
  return api.put(`/journals/${id}`, data)
}
export function deleteJournal(id) {
  return api.delete(`/journals/${id}`)
}

// ========== 论文 ==========
export function getPapers(params = {}) {
  return api.get('/papers', { params })
}
export function getStarredPapers() {
  return api.get('/papers/starred')
}
export function getPaperDetail(id) {
  return api.get(`/papers/${id}`)
}
export function updatePaperStatus(id, data) {
  return api.patch(`/papers/${id}`, data)
}

export default api
