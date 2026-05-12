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
      redirect: '/'
    },
    {
      path: '/nexa-admin',
      redirect: '/'
    },
    // NEXA_ROUTES
  ]
})

export default router

