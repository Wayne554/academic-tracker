import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import PaperListView from '../views/PaperListView.vue'
import StarredView from '../views/StarredView.vue'
import JournalManageView from '../views/JournalManageView.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: LoginView, meta: { guest: true } },
  { path: '/', name: 'Papers', component: PaperListView, meta: { requiresAuth: true } },
  { path: '/starred', name: 'Starred', component: StarredView, meta: { requiresAuth: true } },
  { path: '/journals', name: 'Journals', component: JournalManageView, meta: { requiresAuth: true, requiresAdmin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    next('/login')
  } else if (to.meta.guest && auth.token) {
    next('/')
  } else if (to.meta.requiresAdmin && !auth.user?.is_admin) {
    next('/')
  } else {
    next()
  }
})

export default router
