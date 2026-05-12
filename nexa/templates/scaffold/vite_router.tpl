import { createRouter, createWebHistory } from 'vue-router'
// NEXA_ROUTE_IMPORTS

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

export default router

