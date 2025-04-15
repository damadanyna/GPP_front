// router/index.ts

import { createRouter, createWebHistory } from 'vue-router/auto'
import { routes } from 'vue-router/auto-routes'
import Cookies from 'js-cookie' // <--- Ajouté

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 🔐 Liste des routes protégées
const protectedRoutes = ['/dashboard', '/profil', '/dec_credit'] // ajoute ce que tu veux

router.beforeEach((to, from, next) => {
  const token = Cookies.get('auth_token')

  if (protectedRoutes.includes(to.path) && !token) {
    next('/login') // Redirection si non authentifié
  } else {
    next()
  }
})

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.('Failed to fetch dynamically imported module')) {
    if (!localStorage.getItem('vuetify:dynamic-reload')) {
      console.log('Reloading page to fix dynamic import error')
      localStorage.setItem('vuetify:dynamic-reload', 'true')
      location.assign(to.fullPath)
    } else {
      console.error('Dynamic import error, reloading page did not fix it', err)
    }
  } else {
    console.error(err)
  }
})

router.isReady().then(() => {
  localStorage.removeItem('vuetify:dynamic-reload')
})

export default router
