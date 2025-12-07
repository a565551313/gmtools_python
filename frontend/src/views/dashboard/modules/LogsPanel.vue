<template>
  <div class="logs-panel">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon bg-slate-100 text-slate-600"><Document /></el-icon>
          <span>操作日志</span>
          <el-button class="ml-auto" circle @click="fetchLogs"><el-icon><Refresh /></el-icon></el-button>
        </div>
      </template>
      <el-table :data="logs" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="action" label="操作" width="150" />
        <el-table-column prop="details" label="详情" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
      <div class="mt-4 flex justify-end">
        <el-pagination 
          layout="prev, pager, next" 
          :total="total" 
          :page-size="pageSize"
          v-model:current-page="currentPage"
          @current-change="fetchLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import request from '@/api/request'
import { Document, Refresh } from '@element-plus/icons-vue'

const logToConsole = inject('logToConsole')

const logs = ref([])
const loading = ref(false)
const total = ref(0)
const pageSize = ref(20)
const currentPage = ref(1)

async function fetchLogs() {
  loading.value = true
  try {
    const res = await request.get('/api/logs', { params: { page: currentPage.value, size: pageSize.value } })
    logs.value = res.data || []
    total.value = res.total || 0
    logToConsole('GET', '/api/logs', 200, res)
  } catch (e) {
    logToConsole('GET', '/api/logs', 0, { error: e.message })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: bold;
}

.header-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
