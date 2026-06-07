import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import MainLayout from '../admin-nexa/components/MainLayout.vue'
import Dashboard from '../admin-nexa/pages/Dashboard.vue'
import DynamicList from '../admin-nexa/pages/DynamicList.vue'

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
      path: '/nexa-admin',
      component: MainLayout,
      children: [
        {
          path: '',
          name: 'admin_dashboard',
          component: Dashboard
        },
        {
          path: 'table/:entity',
          name: 'dynamic_list',
          component: DynamicList
        }
      ]
    }
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
