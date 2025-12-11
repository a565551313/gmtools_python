import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: () => import('@/views/auth/Login.vue')
        },
        {
            path: '/',
            name: 'dashboard',
            component: () => import('@/views/dashboard/Index.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/admin',
            name: 'super-admin',
            component: () => import('@/views/admin/SuperAdmin.vue'),
            meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
            path: '/activity-management',
            name: 'activity-management',
            component: () => import('@/views/admin/modules/ActivityManagementPanel.vue'),
            meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
            path: '/activity/:id',
            name: 'activity-participation',
            component: () => import('@/views/ActivityParticipation.vue')
        }
    ]
})

router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isLoggedIn) {
        next('/login')
    } else if (to.path === '/login' && authStore.isLoggedIn) {
        next('/')
    } else if (to.meta.requiresAdmin) {
        // Try to fetch user if logged in but no user data
        if (authStore.isLoggedIn && !authStore.user) {
            try {
                await authStore.fetchUser()
            } catch (e) {
                next('/login')
                return
            }
        }
        
        // 检查用户是否为管理员
        const user = authStore.user
        const isAdmin = user?.role === 'admin' || user?.role === 'super_admin'
        if (!isAdmin) {
            // 普通用户无法访问管理员页面，重定向到首页
            next('/')
        } else {
            next()
        }
    } else {
        // Try to fetch user if logged in but no user data
        if (authStore.isLoggedIn && !authStore.user) {
            try {
                await authStore.fetchUser()
                next()
            } catch (e) {
                next('/login')
            }
        } else {
            next()
        }
    }
})

export default router
