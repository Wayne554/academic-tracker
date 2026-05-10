import { create } from 'zustand'
import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const useStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  loading: false,

  login: async (email, password) => {
    set({ loading: true })
    try {
      console.log('尝试登录...', email)
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)
      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      console.log('登录响应:', response.data)
      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      set({ token: access_token })
      await get().fetchMe()
    } catch (error) {
      console.error('登录错误:', error)
      throw error
    } finally {
      set({ loading: false })
    }
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ token: null, user: null })
  },

  fetchMe: async () => {
    try {
      const response = await api.get('/auth/me')
      set({ user: response.data })
    } catch (error) {
      localStorage.removeItem('token')
      set({ token: null, user: null })
    }
  }
}))

export { api }
