import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const service = axios.create({
    baseURL: '', // Proxy handles this
    timeout: 10000
})

// Request interceptor
service.interceptors.request.use(
    config => {
        const authStore = useAuthStore()
        if (authStore.token) {
            config.headers['Authorization'] = `Bearer ${authStore.token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// Response interceptor
service.interceptors.response.use(
    response => {
        const res = response.data
        // You might want to check custom codes here if your backend returns { code: 200, data: ... }
        // But based on user-functions.html, it seems to rely on HTTP status mostly, or checks res.status === 'success'
        return res
    },
    error => {
        console.log('err' + error)
        let message = error.message
        if (error.response && error.response.data) {
            message = error.response.data.detail || error.response.data.message || message
        }
        ElMessage({
            message: message,
            type: 'error',
            duration: 5 * 1000
        })

        if (error.response && error.response.status === 401) {
            const authStore = useAuthStore()
            authStore.logout()
            // router.push('/login') // Might need to import router or handle in store
        }
        return Promise.reject(error)
    }
)

export default service
