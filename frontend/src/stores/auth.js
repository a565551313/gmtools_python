import { defineStore } from 'pinia'
import request from '@/api/request'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('access_token') || '',
        user: null
    }),
    getters: {
        isLoggedIn: (state) => !!state.token
    },
    actions: {
        async login(username, password) {
            try {
                const res = await request.post('/api/users/login', { username, password })
                this.token = res.access_token
                this.user = res.user
                localStorage.setItem('access_token', this.token)
                return res
            } catch (error) {
                throw error
            }
        },
        async fetchUser() {
            try {
                const res = await request.get('/api/users/me')
                this.user = res.user
            } catch (error) {
                this.logout()
            }
        },
        logout() {
            this.token = ''
            this.user = null
            localStorage.removeItem('access_token')
            // Redirect to login handled by component or router
        }
    }
})
