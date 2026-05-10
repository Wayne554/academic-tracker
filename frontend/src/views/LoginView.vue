<template>
  <div class="login-wrap">
    <div class="login-card">
      <h1>📚 Academic Tracker</h1>
      <p class="subtitle">登录以访问你的学术期刊追踪器</p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="username" type="text" required placeholder="请输入用户名" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" required placeholder="请输入密码" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
      </form>
      <p class="hint">默认账号：admin / admin123（登录后请修改密码）</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5; }
.login-card { background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,.1); width: 380px; }
h1 { text-align: center; margin-bottom: 4px; }
.subtitle { text-align: center; color: #888; margin-bottom: 24px; font-size: 14px; }
.form-group { margin-bottom: 16px; }
label { display: block; margin-bottom: 6px; font-size: 14px; color: #333; }
input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
input:focus { outline: none; border-color: #1a73e8; }
button { width: 100%; padding: 12px; background: #1a73e8; color: #fff; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; margin-top: 8px; }
button:disabled { opacity: .6; cursor: not-allowed; }
.error-msg { color: #d93025; font-size: 13px; margin-bottom: 8px; }
.hint { margin-top: 16px; font-size: 12px; color: #aaa; text-align: center; }
</style>
