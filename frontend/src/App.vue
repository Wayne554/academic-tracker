<template>
  <div id="app-root">
    <nav v-if="isLoggedIn" class="navbar">
      <span class="nav-brand">📚 Academic Tracker</span>
      <div class="nav-links">
        <router-link to="/">论文列表</router-link>
        <router-link to="/starred">⭐ 星标论文</router-link>
        <router-link v-if="isAdmin" to="/journals">期刊管理</router-link>
        <a href="#" @click.prevent="logout" class="nav-logout">退出</a>
      </div>
    </nav>
    <main :class="{'with-nav': isLoggedIn}">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const auth = useAuthStore()

const isLoggedIn = computed(() => !!auth.token)
const isAdmin = computed(() => auth.user?.is_admin)

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f6fa; color: #222; }
.navbar { display: flex; align-items: center; justify-content: space-between; padding: 0 24px; height: 56px; background: #1a73e8; color: #fff; }
.nav-brand { font-weight: 700; font-size: 18px; }
.nav-links { display: flex; gap: 20px; align-items: center; }
.nav-links a { color: #fff; text-decoration: none; font-size: 14px; opacity: 0.85; }
.nav-links a:hover, .nav-links a.router-link-active { opacity: 1; text-decoration: underline; }
.nav-logout { cursor: pointer; }
.with-nav { padding-top: 56px; }
main { max-width: 1100px; margin: 0 auto; padding: 24px; }
</style>
