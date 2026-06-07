import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
// NEXA_ROUTE_IMPORTS

// Configure NProgress
NProgress.configure({ showSpinner: false })

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../pages/Home.vue')
    },
    {
      path: '/admin-nexa',
      name: 'admin_dashboard_alias',
      component: () => import('../admin-nexa/pages/Dashboard.vue')
    },
    {
      path: '/nexa-admin',
      name: 'admin_dashboard',
      component: () => import('../admin-nexa/pages/Dashboard.vue')
    },
    // NEXA_ROUTES
  ]
})

router.beforeEach((to, from, next) => {
  if (to.path !== from.path) {
    NProgress.start()
  }
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
