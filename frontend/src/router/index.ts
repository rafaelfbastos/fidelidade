import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Auth/LoginView.vue'),
      meta: {
        layout: 'auth',
        requiresAuth: false,
      },
    },
    {
      path: '/select-company',
      name: 'company-select',
      component: () => import('../views/Auth/CompanySelectorView.vue'),
      meta: {
        requiresAuth: true,
        layout: 'auth',
        allowWithoutCompany: true,
      },
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/settings/layout',
      name: 'layout-settings',
      component: () => import('../views/Settings/LayoutSettingsView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/settings/users',
      name: 'company-users',
      component: () => import('../views/Settings/CompanyUsersView.vue'),
      meta: {
        requiresAuth: true,
        requiresCompanyRole: ['owner', 'admin'],
      },
    },
    {
      path: '/profile',
      name: 'user-profile',
      component: () => import('../views/Profile/UserProfileView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/Errors/NotFoundView.vue'),
      meta: {
        requiresAuth: false,
      },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login' })
  }

  const needsCompanySelection =
    authStore.isAuthenticated &&
    !authStore.selectedCompany &&
    (authStore.user?.companies?.length ?? 0) > 1

  if (to.meta.requiresAuth && !to.meta.allowWithoutCompany && needsCompanySelection && to.name !== 'company-select') {
    return next({ name: 'company-select' })
  }

  const requiredRoles = to.meta.requiresCompanyRole as string[] | undefined
  if (to.meta.requiresAuth && requiredRoles?.length) {
    const currentRole = authStore.selectedCompany?.role
    if (!currentRole || !requiredRoles.includes(currentRole)) {
      return next({ name: 'dashboard' })
    }
  }

  if (to.name === 'login' && authStore.isAuthenticated) {
    return next({ name: 'dashboard' })
  }

  return next()
})

export default router
