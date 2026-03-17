import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory('/bhangrabot'),
  routes,
})

// Navigation guard to check auth
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    try {
      const response = await fetch('/auth/me', { credentials: 'include' })
      if (response.ok) {
        next()
      } else {
        next('/login')
      }
    } catch {
      next('/login')
    }
  } else {
    next()
  }
})

export default router
